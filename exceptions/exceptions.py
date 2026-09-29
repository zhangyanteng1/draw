class TokenExpiredError(Exception):
    """Cookie / Token 失效（HTTP 401）"""


class BusinessError(Exception):
    """业务逻辑校验异常"""


class LoginEnvError(Exception):
    """登录环境异常，需要二次身份验证"""
