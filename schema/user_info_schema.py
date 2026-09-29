from datetime import datetime
from typing import Optional

from pydantic import BaseModel, ConfigDict, Field

from const.user_const import UserConst
from tool.date_utils import DateUtils


class UserInfoCreate(BaseModel):
    """创建用户信息入参"""
    user_id: int
    real_name: str = Field(default_factory=lambda: UserConst.DEFAULT_REAL_NAME % int(DateUtils.get_current_timestamp()))
    avatar: str = UserConst.DEFAULT_REAL_AVATAR
    sex: int = 0
    address: str = ""
    phone: str = ""
    email: str = ""
    wechat: str = ""
    desc: Optional[str] = None


class UserInfoUpdate(BaseModel):
    """更新用户信息入参"""
    real_name: Optional[str] = None
    avatar: Optional[str] = None
    sex: Optional[int] = None
    address: Optional[str] = None
    phone: Optional[str] = None
    email: Optional[str] = None
    wechat: Optional[str] = None
    desc: Optional[str] = None


class UserInfoResponse(BaseModel):
    """用户信息出参"""
    model_config = ConfigDict(from_attributes=True)

    id: int
    user_id: int
    real_name: str
    avatar: str
    sex: Optional[int] = None
    address: str
    phone: str
    email: str
    wechat: str
    desc: Optional[str] = None
    created_time: Optional[datetime] = None
    updated_time: Optional[datetime] = None
