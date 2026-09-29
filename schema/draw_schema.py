from datetime import datetime
from typing import Optional

from pydantic import BaseModel, ConfigDict

from const.draw_const import DrawConst


class DrawCreate(BaseModel):
    """创建抽奖入参"""
    draw_name: str
    status: int = DrawConst.NOT_STARTED
    start_time: datetime
    offline_time: datetime
    desc: Optional[str] = None
    op_id: Optional[int] = None


class DrawUpdate(BaseModel):
    """更新抽奖入参"""
    id: Optional[int] = None
    draw_name: Optional[str] = None
    status: Optional[int] = None
    start_time: Optional[datetime] = None
    offline_time: Optional[datetime] = None
    desc: Optional[str] = None
    up_id: Optional[int] = None


class DrawFilter(BaseModel):
    """查询抽奖入参"""
    id: Optional[int] = None
    status: Optional[int] = None
    page: int = 0
    page_size: int = 10


class DrawResponse(BaseModel):
    """查询抽奖出参"""
    model_config = ConfigDict(from_attributes=True)

    id: Optional[int] = None
    draw_name: Optional[str] = None
    status: Optional[int] = None
    start_time: Optional[datetime] = None
    offline_time: Optional[datetime] = None
    desc: Optional[str] = None
    op_id: Optional[int] = None
    up_id: Optional[int] = None
    created_time: Optional[datetime] = None
    updated_time: Optional[datetime] = None






