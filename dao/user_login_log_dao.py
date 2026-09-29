from typing import Optional

from sqlalchemy.orm import Session

from model.user_login_log import UserLoginLog
from schema.user_login_log_schema import UserLoginLogCreate, UserLoginLogFilter


class UserLoginLogDao:

    @staticmethod
    def insert(db: Session, log_create: UserLoginLogCreate) -> UserLoginLog:
        log = UserLoginLog(**log_create.model_dump())
        db.add(log)
        db.flush()
        db.refresh(log)
        return log

    @staticmethod
    def get_list(db: Session, log_filter: UserLoginLogFilter) -> tuple[list[UserLoginLog], int]:
        query = db.query(UserLoginLog).order_by(UserLoginLog.login_time.desc())

        if log_filter.user_id:
            query = query.filter(UserLoginLog.user_id == log_filter.user_id)

        total = query.count()
        offset = (log_filter.page - 1) * log_filter.page_size
        items = query.offset(offset).limit(log_filter.page_size).all()
        return items, total

    @staticmethod
    def get_latest_by_user_id(db: Session, user_id: int) -> Optional[UserLoginLog]:
        return (
            db.query(UserLoginLog)
            .filter(UserLoginLog.user_id == user_id)
            .order_by(UserLoginLog.login_time.desc())
            .first()
        )
