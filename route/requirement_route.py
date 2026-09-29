from fastapi import APIRouter, Depends, Request
from sqlalchemy.orm import Session

from common.response import Response
from db.session import get_db
from schema.requirement_schema import RequirementCreate, RequirementUpdate
from service.requirement_service import RequirementService

requirement_router = APIRouter(prefix="/requirement")


# 创建需求
@requirement_router.post("/create")
def create(req: RequirementCreate, request: Request, db: Session = Depends(get_db)):
    result = RequirementService.create_requirement(db, req, request.state.user_id)
    return Response.success(message="创建成功", data=result)


# 更新需求
@requirement_router.post("/update")
def update(req: RequirementUpdate, request: Request, db: Session = Depends(get_db)):
    result = RequirementService.update_requirement(db, req.req_id, req, request.state.user_id)
    return Response.success(message="更新成功", data=result)
