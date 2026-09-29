from fastapi import APIRouter, Depends, Request
from sqlalchemy.orm import Session

from common.response import Response
from const.draw_const import DrawConst
from db.session import get_db
from schema.draw_schema import DrawCreate, DrawUpdate
from service.draw_service import DrawService

draw_router = APIRouter(prefix="/draw")


# 创建抽奖活动
@draw_router.post("/create")
def create(req: DrawCreate, request: Request, db: Session = Depends(get_db)):
    DrawService.save_draw(db, req, request.state.user_id)
    return Response.success(message="活动创建成功")


# 更新抽奖活动
@draw_router.post("/update")
def update(req: DrawUpdate, request: Request, db: Session = Depends(get_db)):
    DrawService.update_draw(db, req.id, req, request.state.user_id)
    return Response.success(message="活动更新成功")


# 活动上线
@draw_router.get("/online")
def online(draw_id: int, request: Request, db: Session = Depends(get_db)):
    DrawService.draw_online(db, draw_id, request.state.user_id)
    return Response.success(message="活动上线成功")


# 活动下线
@draw_router.get("/offline")
def offline(draw_id: int, request: Request, db: Session = Depends(get_db)):
    DrawService.draw_offline(db, draw_id, request.state.user_id)
    return Response.success(message="活动下线成功")


# 抽奖
@draw_router.get("/draw_get")
def draw(draw_id: int, request: Request, db: Session = Depends(get_db)):
    result = DrawService.draw_get(db, draw_id, request.state.user_id)

    if result.prize_sku == DrawConst.NOT_WIN_PRIZE_SKU:
        return Response.success(message=f"{result.draw_name}继续努力", data=result)

    return Response.success(message=f"恭喜您抽中:{result.draw_name}", data=result)
