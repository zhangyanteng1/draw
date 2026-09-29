from fastapi import APIRouter, Depends, Request
from sqlalchemy.orm import Session

from common.response import Response
from db.session import get_db
from schema.draw_prize_schema import DrawPrizeCreateList, DrawPrizeUpdateList
from service.draw_prize_service import DrawPrizeService

draw_prize_router = APIRouter(prefix="/draw_prize")


# 添加抽奖奖品
@draw_prize_router.post("/create")
def create(req: DrawPrizeCreateList, request: Request, db: Session = Depends(get_db)):
    DrawPrizeService.save_draw_prize(db, req, request.state.user_id)
    return Response.success(message="奖品关联成功")


# 更新抽奖奖品
@draw_prize_router.post("/update")
def create(req: DrawPrizeUpdateList, request: Request, db: Session = Depends(get_db)):
    DrawPrizeService.update_draw_prize(db, req, request.state.user_id)
    return Response.success(message="奖品更新成功")






