from datetime import datetime
from typing import Optional

from pydantic import BaseModel, ConfigDict


class UserLoginLogCreate(BaseModel):
    """创建登录日志入参"""
    user_id: int
    ip: Optional[str] = None
    device_name: Optional[str] = None
    device_type: Optional[int] = None
    os: Optional[str] = None


class UserLoginLogFilter(BaseModel):
    """查询登录日志入参"""
    user_id: Optional[int] = None
    page: int = 1
    page_size: int = 10


class UserLoginLogResponse(BaseModel):
    """登录日志出参"""
    model_config = ConfigDict(from_attributes=True)

    id: int
    user_id: int
    ip: Optional[str] = None
    device_name: Optional[str] = None
    device_type: Optional[int] = None
    os: Optional[str] = None
    login_time: Optional[datetime] = None
