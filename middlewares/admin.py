from fastapi import Header

from exceptions.exceptions import TokenExpiredError
from tool.jwt_utils import JwtUtils


def format_user(authorization: str = Header(None)) -> dict:
    if not authorization:
        raise TokenExpiredError("access_token为空")
    payload = JwtUtils.verify_token_safe(authorization)
    return {"user_id": payload["user_id"], "access_token": authorization}
