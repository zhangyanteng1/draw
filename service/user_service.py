import logging
import time
from typing import Optional

from fastapi import Request
from sqlalchemy.orm import Session
from cache.user_cache import UserCache
from const.user_cache_key import UserCacheKey
from dao.user_dao import UserDao
from dao.user_info_dao import UserInfoDao
from dao.user_login_log_dao import UserLoginLogDao
from exceptions.exceptions import BusinessError, LoginEnvError
from model.user import User
from schema.user_info_schema import UserInfoCreate
from schema.user_login_log_schema import UserLoginLogCreate
from schema.user_schema import UserCreate, RegisterUser, LoginUser, UserFilter, UserInfoResponse
from tool.ip_utils import IpUtils
from tool.jwt_utils import JwtUtils
from tool.user_utils import UserUtils

logger = logging.getLogger(__name__)


class UserService:

    @staticmethod
    def register_user(db: Session, req: RegisterUser):
        username = req.username.strip()
        password = req.password.strip()
        if not username or not password:
            raise BusinessError("用户名或密码不能为空")

        if len(username) < 6 or len(password) < 6:
            raise BusinessError("用户名或密码长度小于6位数")

        user = UserDao.get_by_username(db, username)
        if user:
            raise BusinessError("用户名已存在")
        UserService.save_user(db, req)

    @staticmethod
    def save_user(db: Session, req: RegisterUser):
        try:
            user_create = UserCreate(
                user_id=UserUtils.generate_user_id(),
                username=req.username,
                password=UserUtils.hash_password_argon2(req.password)
            )
            user = UserDao.insert(db, user_create)

            user_info = UserInfoCreate(user_id=user.user_id)
            UserInfoDao.insert(db, user_info)

            db.commit()
        except Exception as e:
            logger.error(f"用户注册错误: {str(e)}")
            db.rollback()
            raise

    @staticmethod
    def login_user(db: Session, req: LoginUser, request: Request) -> dict[str, str]:
        username = req.username.strip()
        password = req.password.strip()

        # 用户名和密码非空校验
        if not username or not password:
            raise BusinessError("用户名或密码为空")

        # 前置校验错误次数限制
        UserService.check_error_number(username, request)

        # 校验用户名和密码是否正确
        user = UserService.check_login_user(db, username, password, request)

        # 校验登录环境（IP + 设备名，均不一致才触发）
        ip = IpUtils.get_client_ip(request)
        UserService.check_login_env(db, user.user_id, ip, req.device_name)

        # 插入登录日志（不阻断登录流程）
        try:
            log_create = UserLoginLogCreate(
                user_id=user.user_id,
                ip=ip,
                device_name=req.device_name,
                device_type=req.device_type,
                os=req.os
            )
            UserLoginLogDao.insert(db, log_create)
            db.commit()
        except Exception as e:
            db.rollback()
            logger.error(f"插入登录日志失败 user_id={user.user_id}, error={e}")

        # 校验通过生成token
        return UserService.create_token(user)

    @staticmethod
    def create_token(user: User) -> dict[str, str]:
        user_id = user.user_id
        payload = {"user_id": user_id}

        # 先查询旧token是否存在, 存在删除避免双token
        is_refresh_token = UserCache().get_refresh_token(user_id)
        if is_refresh_token:
            UserCache().delete_refresh_token(user_id)

        # 生成新的token
        refresh_token = JwtUtils.create_refresh_token(payload)
        access_token = JwtUtils.create_access_token(payload)

        if not refresh_token or not access_token:
            raise BusinessError("登录异常请稍后重试")

        UserCache().set_refresh_token(user_id, refresh_token)
        user_result = {
            "access_token": access_token,
            "refresh_token": refresh_token
        }
        return user_result

    @staticmethod
    def check_login_user(db: Session, username: str, password: str,
                         request: Request) -> Optional[User]:

        user = UserDao.get_by_username(db, username)
        if not user:
            # 用户名不存在，只记录 IP 维度（防枚举账号）
            UserService.set_ip_error(request)
            raise BusinessError("用户名或密码错误")

        check_pwd = UserUtils.verify_password_argon2(password, user.password)
        if not check_pwd:
            # 密码错误，同时记录 username + IP 维度（防暴力破解）
            UserService.set_login_error(username, request)
            raise BusinessError("用户名或密码错误")

        return user

    @staticmethod
    def set_ip_error(request: Request):
        ip = IpUtils.get_client_ip(request)
        is_ip_error = UserCache().set_login_error(UserCacheKey.USER_LOGIN_BLACK % ip)
        if not is_ip_error:
            raise BusinessError("登录错误请稍后重试")

    @staticmethod
    def set_login_error(username: str, request: Request):
        # 存储 username 维度错误次数
        is_login_error = UserCache().set_login_error(UserCacheKey.USER_LOGIN_ERROR % username)
        if not is_login_error:
            raise BusinessError("登录错误请稍后重试")

        # 存储 IP 维度错误次数
        UserService.set_ip_error(request)

    @staticmethod
    def check_login_env(db: Session, user_id: int, ip: str, device_name: Optional[str]):
        last_log = UserLoginLogDao.get_latest_by_user_id(db, user_id)
        if not last_log:
            return
        ip_changed = last_log.ip != ip
        device_changed = last_log.device_name != device_name
        if ip_changed and device_changed:
            raise LoginEnvError("登录环境异常，请进行身份验证")

    @staticmethod
    def check_error_number(username: str, request: Request):
        # 先校验ip限制
        ip = IpUtils.get_client_ip(request)
        error_number = UserCache().get_login_error(UserCacheKey.USER_LOGIN_BLACK % ip)
        if error_number >= 5:
            raise BusinessError("当前设备限制登录,请5分钟后重试")

        error_number = UserCache().get_login_error(UserCacheKey.USER_LOGIN_ERROR % username)
        if error_number >= 5:
            raise BusinessError("错误次数过多,请5分钟后重试")

    @staticmethod
    def logout_user(user_id: int, access_token: str):
        # 将 access_token 加入黑名单，TTL = 剩余有效时间
        try:
            payload = JwtUtils.verify_token(access_token)
            remaining = int(payload.get("exp", 0) - time.time())
            if remaining > 0:
                UserCache().set_blacklist_token(access_token, remaining)
        except Exception:
            pass
        UserCache().delete_refresh_token(user_id)

    @staticmethod
    def refresh_token(refresh_token: str) -> str:
        payload = JwtUtils.verify_token_safe(refresh_token, token_type="refresh")
        user_id = payload.get("user_id")

        cached_token = UserCache().get_refresh_token(user_id)
        if not cached_token or cached_token != refresh_token:
            raise BusinessError("refresh token已失效，请重新登录")

        return JwtUtils.create_access_token({"user_id": user_id})

    @staticmethod
    def get_user_info(db: Session, user_id: int) -> UserInfoResponse:
        logger.info("测试一下日志")
        logger.error("测试一下日志")
        logger.warning("测试一下日志")
        user = UserDao.get_by_user_id(db, user_id)
        if not user:
            raise BusinessError("用户不存在")

        user_info = UserInfoDao.get_by_user_id(db, user_id)
        return UserInfoResponse(
            user_id=user.user_id,
            username=user.username,
            status=user.status,
            created_time=user.created_time,
            real_name=user_info.real_name if user_info else None,
            avatar=user_info.avatar if user_info else None,
            sex=user_info.sex if user_info else None,
            address=user_info.address if user_info else None,
            phone=user_info.phone if user_info else None,
            email=user_info.email if user_info else None,
            wechat=user_info.wechat if user_info else None,
            desc=user_info.desc if user_info else None,
        )

