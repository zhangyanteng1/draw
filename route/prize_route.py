from fastapi import APIRouter, Depends, Request
from sqlalchemy.orm import Session

from common.response import Response
from db.session import get_db
from schema.prize_schema import PrizeCreate, PrizeUpdate
from service.prize_service import PrizeService

prize_router = APIRouter(prefix="/prize")


# 添加奖品
@prize_router.post("/create")
def create(req: PrizeCreate, request: Request, db: Session = Depends(get_db)):
    PrizeService.save_prize(db, req, request.state.user_id)
    return Response.success(message="奖品添加成功")


# 更新奖品
@prize_router.post("/update")
def update(req: PrizeUpdate, request: Request, db: Session = Depends(get_db)):
    PrizeService.update_prize(db, req.id, req, request.state.user_id)
    return Response.success(message="奖品更新成功")




