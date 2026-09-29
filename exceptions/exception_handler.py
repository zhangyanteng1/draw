import logging

from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError

from common.response import Response
from common.status import Status
from exceptions.exceptions import BusinessError, LoginEnvError, TokenExpiredError

logger = logging.getLogger(__name__)


def register_exception_handlers(app: FastAPI):

    @app.exception_handler(RequestValidationError)
    async def validation_exception_handler(request: Request, exc: RequestValidationError):
        return Response.json_response(code=Status.PARAM_ERROR, message="参数不合法")

    @app.exception_handler(TokenExpiredError)
    async def token_exception_handler(request: Request, exc: TokenExpiredError):
        return Response.json_response(code=Status.TOKEN_EXPIRED, message=str(exc))

    @app.exception_handler(BusinessError)
    async def business_exception_handler(request: Request, exc: BusinessError):
        return Response.json_response(code=Status.BUSINESS_ERROR, message=str(exc))

    @app.exception_handler(LoginEnvError)
    async def login_env_exception_handler(request: Request, exc: LoginEnvError):
        return Response.json_response(code=Status.LOGIN_ENV_ERROR, message=str(exc))

    @app.exception_handler(Exception)
    async def global_exception_handler(request: Request, exc: Exception):
        logger.error(f"内部异常 path={request.url.path} error={exc}", exc_info=True)
        return Response.json_response(code=Status.ERROR, message="服务器内部错误")
