from typing import Optional

from sqlalchemy import and_
from sqlalchemy.orm import Session
from model.user import User
from schema.user_schema import UserCreate, UserUpdate, UserFilter


class UserDao:

    @staticmethod
    def insert(db: Session, user_create: UserCreate) -> User:
        user = User(**user_create.model_dump())
        db.add(user)
        db.flush()
        db.refresh(user)
        return user

    @staticmethod
    def get_by_user_id(db: Session, user_id: int) -> Optional[User]:
        return db.query(User).filter(User.user_id == user_id).first()

    @staticmethod
    def get_by_username(db: Session, username: str) -> Optional[User]:
        return db.query(User).filter(User.username == username).first()

    @staticmethod
    def query_user_list(db: Session) -> list[User]:
        return db.query(User).order_by(User.id.desc()).all()

    @staticmethod
    def get_list(db: Session, user_filter: UserFilter) -> list[User]:
        conditions = []
        if user_filter.user_id:
            conditions.append(User.user_id == user_filter.user_id)

        if user_filter.username:
            conditions.append(User.username == user_filter.username)

        if user_filter.password:
            conditions.append(User.password == user_filter.password)

        if user_filter.status:
            conditions.append(User.status == user_filter.status)

        if user_filter.start_created_time and user_filter.end_created_time:
            conditions.append(User.created_time.between(user_filter.start_created_time,
                                                        user_filter.end_created_time))
        query = db.query(User).order_by(User.id.desc()).filter(and_(*conditions))
        return query.all()

    @staticmethod
    def update(db: Session, user: User, user_update: UserUpdate) -> Optional[User]:
        for field, value in user_update.model_dump(exclude_unset=True).items():
            setattr(user, field, value)
        return user
