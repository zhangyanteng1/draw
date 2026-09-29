from sqlalchemy.orm import Session

from dao.requirement_dao import RequirementDao
from exceptions.exceptions import BusinessError
from schema.requirement_schema import RequirementCreate, RequirementUpdate, RequirementResponse


class RequirementService:

    @staticmethod
    def create_requirement(db: Session, req_create: RequirementCreate, user_id: int) -> RequirementResponse:
        if RequirementDao.get_by_req_id(db, req_create.req_id):
            raise BusinessError("需求id已存在")
        req_create.op_id = user_id
        requirement = RequirementDao.insert(db, req_create)
        db.commit()
        return RequirementResponse.model_validate(requirement)

    @staticmethod
    def update_requirement(db: Session, req_id: str, req_update: RequirementUpdate, user_id: int) -> RequirementResponse:
        requirement = RequirementDao.get_by_req_id(db, req_id)
        if not requirement:
            raise BusinessError("需求不存在")
        req_update.up_id = user_id
        requirement = RequirementDao.update(db, requirement, req_update)
        db.commit()
        return RequirementResponse.model_validate(requirement)
