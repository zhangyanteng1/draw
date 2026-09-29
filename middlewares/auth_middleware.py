import logging
from fastapi import Request

from cache.user_cache import UserCache
from common.response import Response
from common.status import Status
from exceptions.exceptions import TokenExpiredError
from tool.jwt_utils import JwtUtils
from tool.yaml_utils import get_app_config


_NO_AUTHORIZE_API = get_app_config("no_authorize_api")

logger = logging.getLogger(__name__)


# 全局鉴权中间件
async def auth_middleware(request: Request, call_next):

    try:
        # 获取请求路径
        request_path = request.url.path

        # 白名单校验
        if request_path in _NO_AUTHORIZE_API:
            response = await call_next(request)
            return response
        # 先从cookie获取
        authorization = request.cookies.get("authorization")

        # cookie不存在从请求头获取
        if not authorization:
            authorization = request.headers.get("authorization")

        # 都不存在则返回登录失效
        if not authorization:
            return Response.json_response(code=Status.TOKEN_EXPIRED, message="access_token为空")

        # 验证 access_token 有效性
        payload = JwtUtils.verify_token_safe(authorization)

        # 检查是否在黑名单（已退出登录）
        if UserCache().is_blacklist_token(authorization):
            return Response.json_response(code=Status.TOKEN_EXPIRED, message="token已失效，请重新登录")

        # 将用户信息注入 request.state，业务层直接读取，无需重复解析
        request.state.user_id = payload["user_id"]
        request.state.access_token = authorization

        response = await call_next(request)
        return response
    except TokenExpiredError as e:
        return Response.json_response(code=Status.TOKEN_EXPIRED, message=str(e))
    # except Exception as e:
    #     logger.error(f"验证access_token出错: {e}")
    #     return Response.json_response(code=Status.TOKEN_EXPIRED, message="验证access_token出错")
