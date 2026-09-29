from datetime import datetime
from typing import Optional, List
from pydantic import BaseModel, ConfigDict

from schema.page_schema import Total, PageModel


class UserDrawAdd(BaseModel):
    """添加抽奖次数"""
    user_id: Optional[int] = None
    draw_id: Optional[int] = None
    total_quota: int = 1
    used_times: int = 0


class UserDrawFilter(PageModel):
    """查询抽奖次数"""
    user_id: Optional[int] = None
    draw_id: Optional[int] = None


class UserDrawResponse(BaseModel):
    """查询抽奖次数出参"""
    model_config = ConfigDict(from_attributes=True)

    user_id: Optional[int] = None
    draw_id: Optional[int] = None
    total_quota: Optional[int] = None
    used_times: Optional[int] = None
    created_time: Optional[datetime] = None
    updated_time: Optional[datetime] = None


class UserDrawListResponse(Total):
    list: List[UserDrawResponse] = []


class DrawQualification(BaseModel):
    """抽奖资格响应模型"""
    is_draw: bool = False
    draw_number: int = 0
