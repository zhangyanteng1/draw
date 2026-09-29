from fastapi import APIRouter, Depends, Request
from sqlalchemy.orm import Session
from common.response import Response
from db.session import get_db
from schema.user_draw_schema import UserDrawAdd, UserDrawFilter
from service.user_draw_service import UserDrawService

user_draw_router = APIRouter(prefix="/user_draw")


# 添加抽奖次数
@user_draw_router.post("/add")
def add(req: UserDrawAdd, request: Request, db: Session = Depends(get_db)):
    UserDrawService.save_or_update_user_draw(db, req, request.state.user_id)
    return Response.success(message="添加抽奖次数成功")


# 查询抽奖次数
@user_draw_router.post("/get")
def get(req: UserDrawFilter, db: Session = Depends(get_db)):
    result = UserDrawService.get_user_draw_list(db, req)
    return Response.success(message="查询抽奖次数成功", data=result)


# 查询抽奖资格
@user_draw_router.post("/qualification")
def get_draw_qualification(req: UserDrawFilter, request: Request, db: Session = Depends(get_db)):
    req.user_id = request.state.user_id
    result = UserDrawService.get_draw_qualification(db, req)

    if result.is_draw:
        return Response.success(message="获取抽奖资格成功", data=result)

    return Response.error(message="无抽奖资格", data=result)



