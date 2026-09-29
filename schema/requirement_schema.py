from datetime import datetime
from typing import Optional

from pydantic import BaseModel, ConfigDict


class RequirementCreate(BaseModel):
    """创建需求入参"""
    req_id: str
    req_name: str
    product_users: Optional[str] = None
    dev_users: Optional[str] = None
    test_users: Optional[str] = None
    dev_start_time: Optional[datetime] = None
    dev_end_time: Optional[datetime] = None
    test_start_time: Optional[datetime] = None
    test_end_time: Optional[datetime] = None
    online_time: Optional[datetime] = None
    skip_test: int = 0
    requester: Optional[str] = None
    op_id: Optional[int] = None


class RequirementUpdate(BaseModel):
    """更新需求入参"""
    req_id: str
    req_name: Optional[str] = None
    product_users: Optional[str] = None
    dev_users: Optional[str] = None
    test_users: Optional[str] = None
    dev_start_time: Optional[datetime] = None
    dev_end_time: Optional[datetime] = None
    test_start_time: Optional[datetime] = None
    test_end_time: Optional[datetime] = None
    online_time: Optional[datetime] = None
    skip_test: Optional[int] = None
    requester: Optional[str] = None
    up_id: Optional[int] = None


class RequirementResponse(BaseModel):
    """需求出参"""
    model_config = ConfigDict(from_attributes=True)

    id: int
    req_id: str
    req_name: str
    product_users: Optional[str] = None
    dev_users: Optional[str] = None
    test_users: Optional[str] = None
    dev_start_time: Optional[datetime] = None
    dev_end_time: Optional[datetime] = None
    test_start_time: Optional[datetime] = None
    test_end_time: Optional[datetime] = None
    online_time: Optional[datetime] = None
    skip_test: int
    requester: Optional[str] = None
    op_id: Optional[int] = None
    up_id: Optional[int] = None
    created_time: Optional[datetime] = None
    updated_time: Optional[datetime] = None
