from typing import Optional

from sqlalchemy.orm import Session

from model.requirement import Requirement
from schema.requirement_schema import RequirementCreate, RequirementUpdate


class RequirementDao:

    @staticmethod
    def insert(db: Session, req_create: RequirementCreate) -> Requirement:
        requirement = Requirement(**req_create.model_dump())
        db.add(requirement)
        db.flush()
        db.refresh(requirement)
        return requirement

    @staticmethod
    def update(db: Session, requirement: Requirement, req_update: RequirementUpdate) -> Requirement:
        for field, value in req_update.model_dump(exclude_unset=True).items():
            setattr(requirement, field, value)
        return requirement

    @staticmethod
    def get_by_req_id(db: Session, req_id: str) -> Optional[Requirement]:
        return db.query(Requirement).filter(Requirement.req_id == req_id).first()
