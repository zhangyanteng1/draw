import os

from dotenv import load_dotenv
from fastapi import APIRouter, Depends, Request, Response as Res, Cookie
from sqlalchemy.orm import Session
from common.response import Response
from common.status import Status
from const.user_const import UserConst
from db.session import get_db
from schema.user_schema import RegisterUser, LoginUser, TokenResponse, RefreshToken
from service.user_service import UserService

load_dotenv()

user_router = APIRouter(prefix="/user")

# samesite=none 必须配合 secure=True, 否则浏览器会丢弃 Cookie。
# 本地 HTTP 调试用 secure=False + lax; 生产 HTTPS 设 COOKIE_SECURE=true 即可。
_COOKIE_SECURE = os.getenv("COOKIE_SECURE", "false").lower() == "true"
_COOKIE_SAMESITE = "none" if _COOKIE_SECURE else "lax"


# 注册
@user_router.post("/register")
def register(req: RegisterUser, db: Session = Depends(get_db)):
    UserService.register_user(db, req)
    return Response.success(message="注册成功")


# 登录
@user_router.post("/login")
def login(req: LoginUser, request: Request, response: Res, db: Session = Depends(get_db)):
    user_result = UserService.login_user(db, req, request)
    response.set_cookie(
        key="refresh_token",
        value=user_result['refresh_token'],
        max_age=UserConst.REFRESH_TOKEN_EXPIRE,
        path=UserConst.COOKIE_API_PATH,
        httponly=True,
        secure=_COOKIE_SECURE,
        samesite=_COOKIE_SAMESITE,
        domain=None
    )
    access_token = TokenResponse(
        access_token=user_result['access_token']
    )
    return Response.success(message="登录成功", data=access_token)


# 退出登录
@user_router.post("/logout")
def logout(request: Request):
    UserService.logout_user(request.state.user_id, request.state.access_token)
    return Response.success(message="退出登录成功")


# 刷新 access_token
@user_router.post("/refresh")
def refresh(req: RefreshToken = None, refresh_token: str = Cookie(None)):

    if not refresh_token and req:
        refresh_token = req.refresh_token

    if not refresh_token:
        return Response.error(code=Status.TOKEN_EXPIRED, message="用户未登录")

    access_token = UserService.refresh_token(refresh_token)
    return Response.success(message="刷新成功", data={"access_token": access_token})


# 获取当前用户信息
@user_router.get("/info")
def get_info(request: Request, db: Session = Depends(get_db)):
    user_detail = UserService.get_user_info(db, request.state.user_id)
    return Response.success(data=user_detail)
