from typing import Optional, List

from pydantic import BaseModel, ConfigDict, Field


class DrawPrizeReq(BaseModel):
    """抽奖商品入参"""
    id: Optional[int] = None
    draw_id: Optional[int] = None
    prize_name: str
    prize_sku: str
    prize_type: int
    is_guaranteed: int
    prize_price: int
    prize_inventory: int = 0
    draw_prize_status: int = 1
    reduce_inventory: int = 0
    prize_picture: str
    probability: Optional[int] = None
    op_id: Optional[int] = None
    up_id: Optional[int] = None


class DrawPrizeUpdate(BaseModel):
    """更新抽奖商品"""
    prize_name: Optional[str] = None
    prize_sku: Optional[str] = None
    prize_type: Optional[int] = None
    is_guaranteed: Optional[int] = None
    prize_price: Optional[int] = None
    prize_inventory: Optional[int] = None
    reduce_inventory: Optional[int] = None
    draw_prize_status: Optional[int] = None
    up_id: Optional[int] = None


class DrawPrizeCreateList(BaseModel):
    """创建抽奖商品入参"""
    draw_id: Optional[int] = None
    draw_prize_list: Optional[list[DrawPrizeReq]] = None


class DrawPrizeUpdateList(BaseModel):
    """更新抽奖商品入参"""
    draw_id: Optional[int] = None
    draw_prize_list: Optional[list[DrawPrizeReq]] = None


class DrawPrizeFilter(BaseModel):
    """查询抽奖商品"""
    draw_id: Optional[int] = None
    prize_sku: Optional[str] = None
    prize_type: Optional[int] = None
    is_guaranteed: Optional[int] = None
    draw_prize_status: Optional[int] = None


class DrawPrizeConfig(BaseModel):
    """查询抽奖出参"""
    model_config = ConfigDict(from_attributes=True, populate_by_name=True)

    id: Optional[int] = None
    draw_name: Optional[str] = Field(None, alias='prize_name')
    prize_sku: Optional[str] = Field(None, alias='prize_sku')
    probability: Optional[int] = Field(None, alias='probability')  # 若前后端一致，可省略 Field
    stock: Optional[int] = Field(None, alias='stock')
    is_guaranteed: Optional[int] = Field(None, alias='is_guaranteed')


class DrawPrizesConfigList(BaseModel):
    prizes_config: List[DrawPrizeConfig] = []


