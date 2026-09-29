import datetime
import logging
import os
from typing import Dict, Any, Optional
import jwt
from dotenv import load_dotenv
from exceptions.exceptions import TokenExpiredError

logger = logging.getLogger(__name__)

load_dotenv()


class JwtUtils:

    SECRET_KEY = os.getenv("JWT_SECRET_KEY")
    if not SECRET_KEY:
        raise RuntimeError("环境变量 JWT_SECRET_KEY 未配置，请在 .env 中设置")
    ALGORITHM = "HS256"
    ACCESS_TOKEN_EXPIRE = 3 * 60
    REFRESH_TOKEN_EXPIRE = 24 * 60

    @classmethod
    def _generate_token(cls, payload: Dict[str, Any], expires_delta: datetime.timedelta) -> str:
        """
        内部方法：生成 Token
        :param payload: 自定义载荷（如 user_id, username）
        :param expires_delta: 过期时间增量
        :return: JWT 字符串
        """
        now = datetime.datetime.now(datetime.timezone.utc)
        payload_copy = payload.copy()
        payload_copy.update({
            "exp": now + expires_delta,
            "iat": now,
        })

        return jwt.encode(payload_copy, cls.SECRET_KEY, algorithm=cls.ALGORITHM)

    @classmethod
    def create_access_token(cls, payload: Dict[str, Any]) -> str:
        """
        生成访问令牌（短期有效）
        """
        delta = datetime.timedelta(minutes=cls.ACCESS_TOKEN_EXPIRE)
        return cls._generate_token({**payload, "type": "access"}, delta)

    @classmethod
    def create_refresh_token(cls, payload: Dict[str, Any]) -> str:
        """
        生成刷新令牌（长期有效），通常只包含用户标识，不含权限信息
        """
        delta = datetime.timedelta(minutes=cls.REFRESH_TOKEN_EXPIRE)
        return cls._generate_token({**payload, "type": "refresh"}, delta)

    @classmethod
    def verify_token(cls, token: str, verify_exp: bool = True) -> Dict[str, Any]:
        """
        验证 Token 并返回载荷
        :param token: JWT 字符串
        :param verify_exp: 是否校验过期时间（通常为 True）
        :return: 解码后的载荷字典
        :raises: jwt.ExpiredSignatureError, jwt.InvalidTokenError 等
        """
        options = {"verify_exp": verify_exp}
        # 如果配置了 audience 或 issuer，自动进行验证
        return jwt.decode(
            token,
            cls.SECRET_KEY,
            algorithms=[cls.ALGORITHM],
            options=options,
        )

    @classmethod
    def refresh_access_token(cls, refresh_token: str) -> Dict[str, Any]:
        """
        使用刷新令牌换取新的访问令牌（同时返回新的刷新令牌？此处仅返回新访问令牌）
        实际业务中，可验证刷新令牌后，生成新 access_token 并返回。
        这里只做示范：验证 refresh_token，返回其中的载荷，调用方可根据载荷再生成新 token。
        """
        # 验证刷新令牌（必须验证过期）
        payload = cls.verify_token(refresh_token)
        # 可额外检查 token 类型，例如 payload 中带 "type": "refresh"
        if payload.get("type") != "refresh":
            logger.error(f"Not a refresh token, payload: {payload}")
            raise TokenExpiredError("refresh token不合法")
        # 返回载荷，由调用方生成新的 access_token
        return payload

    # ---------- 辅助方法：统一异常处理 ----------
    @classmethod
    def verify_token_safe(cls, token: str, token_type: str = "access") -> Optional[Dict[str, Any]]:
        """
        验证 Token，校验失败抛出 TokenExpiredError，成功返回载荷
        token_type: "access" 或 "refresh"，用于区分错误提示信息
        """
        token_label = "access_token" if token_type == "access" else "refresh_token"
        try:
            payload = cls.verify_token(token)
            if payload.get("type") != token_type:
                raise TokenExpiredError(f"{token_label}类型不合法")
            return payload
        except jwt.ExpiredSignatureError as e:
            logger.error(f"verify token safe expiredSignature error: {e}")
            raise TokenExpiredError(f"{token_label}已过期")
        except jwt.InvalidTokenError as e:
            logger.error(f"verify token InvalidToken error: {e}")
            raise TokenExpiredError(f"{token_label}不合法")
        except TokenExpiredError:
            raise
        except Exception as e:
            logger.error(f"verify token safe error: {e}")
            raise TokenExpiredError(f"验证{token_label}出错")
