from typing import Optional

from sqlalchemy.orm import Session
from model.user_info import UserInfo
from schema.user_info_schema import UserInfoCreate, UserInfoUpdate


class UserInfoDao:

    @staticmethod
    def insert(db: Session, user_info_create: UserInfoCreate) -> UserInfo:
        user_info = UserInfo(**user_info_create.model_dump())
        db.add(user_info)
        db.flush()
        db.refresh(user_info)
        return user_info

    @staticmethod
    def get_by_user_id(db: Session, user_id: int) -> Optional[UserInfo]:
        return db.query(UserInfo).filter(UserInfo.user_id == user_id).first()

    @staticmethod
    def update(db: Session, user_info: UserInfo, user_info_update: UserInfoUpdate) -> Optional[UserInfo]:
        for field, value in user_info_update.model_dump(exclude_unset=True).items():
            setattr(user_info, field, value)
        return user_info

