from datetime import datetime
from typing import Optional, List
from pydantic import BaseModel, ConfigDict

from schema.page_schema import Total, PageModel


class UserDrawLogFilter(PageModel):
    """查询用户抽奖记录"""
    user_id: Optional[int] = None
    draw_id: Optional[int] = None
    is_win: Optional[int] = None
    prize_name: Optional[str] = None
    prize_sku: Optional[str] = None


class UserDrawLogResponse(BaseModel):
    """查询用户抽奖出参"""
    model_config = ConfigDict(from_attributes=True)

    user_id: Optional[int] = None
    draw_id: Optional[int] = None
    draw_time: Optional[datetime] = None
    is_win: Optional[int] = None
    prize_name: Optional[str] = None
    prize_sku: Optional[str] = None


class UserDrawLogList(Total):
    list: List[UserDrawLogResponse] = []
