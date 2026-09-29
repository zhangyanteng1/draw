from datetime import datetime
from typing import Optional

from pydantic import BaseModel, ConfigDict


class RegisterUser(BaseModel):
    """注册"""
    username: Optional[str] = None
    password: Optional[str] = None


class LoginUser(BaseModel):
    """登录"""
    username: Optional[str] = None
    password: Optional[str] = None
    device_name: Optional[str] = None
    device_type: Optional[int] = None
    os: Optional[str] = None


class UserCreate(BaseModel):
    """创建用户入参"""
    user_id: int
    username: str
    password: str
    status: int = 1


class UserUpdate(BaseModel):
    """更新用户入参"""
    password: Optional[str] = None
    status: Optional[int] = None


class UserFilter(BaseModel):
    """查询用户入参"""
    user_id: Optional[int] = None
    username: Optional[str] = None
    password: Optional[str] = None
    status: Optional[int] = None
    start_created_time: Optional[datetime] = None
    end_created_time: Optional[datetime] = None


class UserResponse(BaseModel):
    """用户出参"""
    model_config = ConfigDict(from_attributes=True)

    id: int
    user_id: Optional[int] = None
    username: str
    status: int
    created_time: Optional[datetime] = None
    updated_time: Optional[datetime] = None


class TokenResponse(BaseModel):
    """登录信息"""
    model_config = ConfigDict(from_attributes=True)

    access_token: Optional[str] = None


class UserInfoResponse(BaseModel):
    """用户详情出参（user + user_info 合并）"""
    user_id: Optional[int] = None
    username: str
    status: int
    real_name: Optional[str] = None
    avatar: Optional[str] = None
    sex: Optional[int] = None
    address: Optional[str] = None
    phone: Optional[str] = None
    email: Optional[str] = None
    wechat: Optional[str] = None
    desc: Optional[str] = None
    created_time: Optional[datetime] = None


class RefreshToken(BaseModel):
    refresh_token: Optional[str] = None

