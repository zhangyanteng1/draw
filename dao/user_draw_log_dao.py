from typing import Tuple, List

from sqlalchemy.orm import Session

from model.user_draw_log import UserDrawLog
from schema.user_draw_log_schema import UserDrawLogFilter


class UserDrawLogDao:

    @staticmethod
    def insert(db: Session, user_draw_log: UserDrawLog) -> UserDrawLog:
        db.add(user_draw_log)
        db.flush()
        db.refresh(user_draw_log)
        return user_draw_log

    @staticmethod
    def query_user_draw_list(db: Session, user_draw_log_filter: UserDrawLogFilter
                             ) -> Tuple[List[UserDrawLog], int]:
        # 构建基础查询（不含分页）
        query = db.query(UserDrawLog).order_by(UserDrawLog.id.desc())

        if user_draw_log_filter.user_id:
            query = query.filter(UserDrawLog.user_id == user_draw_log_filter.user_id)

        if user_draw_log_filter.draw_id:
            query = query.filter(UserDrawLog.draw_id == user_draw_log_filter.draw_id)

        if user_draw_log_filter.is_win:
            query = query.filter(UserDrawLog.is_win == user_draw_log_filter.is_win)

        if user_draw_log_filter.prize_name:
            query = query.filter(UserDrawLog.prize_name.contains(user_draw_log_filter.prize_name))

        if user_draw_log_filter.prize_sku:
            query = query.filter(UserDrawLog.prize_sku == user_draw_log_filter.prize_sku)

        # 先获取总数（在分页前）
        total_count = query.count()

        # 应用分页
        page = user_draw_log_filter.page
        page_size = user_draw_log_filter.page_size
        offset = (page - 1) * page_size
        user_draw_log_list = query.limit(page_size).offset(offset).all()

        return user_draw_log_list, total_count


