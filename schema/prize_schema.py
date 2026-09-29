from datetime import datetime
from decimal import Decimal
from typing import Optional

from pydantic import BaseModel, ConfigDict


class PrizeCreate(BaseModel):
    """创建奖品入参"""
    prize_name: Optional[str] = None
    brand: Optional[str] = None
    prize_sku: Optional[str] = None
    prize_type: int
    image_url: Optional[str] = None
    color: Optional[str] = None
    description: Optional[str] = None
    cost_price: Optional[Decimal] = None
    market_price: Optional[Decimal] = None
    total_stock: int = 0
    remaining_stock: int = 0
    status: int = 1
    op_id: Optional[int] = None


class PrizeUpdate(BaseModel):
    """更新奖品入参"""
    id: Optional[int] = None
    prize_name: Optional[str] = None
    brand: Optional[str] = None
    prize_sku: Optional[str] = None
    prize_type: Optional[int] = None
    color: Optional[str] = None
    image_url: Optional[str] = None
    description: Optional[str] = None
    cost_price: Optional[Decimal] = None
    market_price: Optional[Decimal] = None
    total_stock: Optional[int] = None
    remaining_stock: Optional[int] = None
    status: Optional[int] = None
    up_id: Optional[int] = None


class PrizeFilter(BaseModel):
    """查询奖品入参"""
    id: Optional[int] = None
    prize_type: Optional[int] = None
    status: Optional[int] = None
    prize_sku: Optional[str] = None


class PrizeResponse(BaseModel):
    """查询奖品出参"""
    model_config = ConfigDict(from_attributes=True)

    id: Optional[int] = None
    prize_name: Optional[str] = None
    brand: Optional[str] = None
    prize_sku: Optional[str] = None
    prize_type: Optional[int] = None
    image_url: Optional[str] = None
    description: Optional[str] = None
    cost_price: Optional[Decimal] = None
    market_price: Optional[Decimal] = None
    total_stock: Optional[int] = None
    remaining_stock: Optional[int] = None
    status: Optional[int] = None
    op_id: Optional[int] = None
    up_id: Optional[int] = None
    created_time: Optional[datetime] = None
    updated_time: Optional[datetime] = None

