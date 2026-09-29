from typing import Optional, Tuple, List
from sqlalchemy.orm import Session
from model.user_draw import UserDraw
from schema.user_draw_schema import UserDrawAdd, UserDrawFilter


class UserDrawDao:

    @staticmethod
    def insert(db: Session, user_draw_add: UserDrawAdd) -> UserDraw:
        user_draw = UserDraw(**user_draw_add.model_dump())
        db.add(user_draw)
        db.flush()
        db.refresh(user_draw)
        return user_draw

    @staticmethod
    def get_by_user_draw(db: Session, user_draw_filter: UserDrawFilter) -> Optional[UserDraw]:
        query = db.query(UserDraw).order_by(UserDraw.id.desc())

        if user_draw_filter.user_id:
            query = query.filter(UserDraw.user_id == user_draw_filter.user_id)

        if user_draw_filter.draw_id:
            query = query.filter(UserDraw.draw_id == user_draw_filter.draw_id)

        return query.first()

    @staticmethod
    def query_user_draw_list(db: Session, user_draw_filter: UserDrawFilter) -> Tuple[List[UserDraw], int]:
        # 构建基础查询（不含分页）
        query = db.query(UserDraw).order_by(UserDraw.id.desc())

        if user_draw_filter.user_id:
            query = query.filter(UserDraw.user_id == user_draw_filter.user_id)
        if user_draw_filter.draw_id:
            query = query.filter(UserDraw.draw_id == user_draw_filter.draw_id)

        # 先获取总数（在分页前）
        total_count = query.count()

        # 应用分页
        page = user_draw_filter.page
        page_size = user_draw_filter.page_size
        offset = (page - 1) * page_size
        user_draw_list = query.limit(page_size).offset(offset).all()

        return user_draw_list, total_count

    @staticmethod
    def update(db: Session, user_draw: UserDraw, user_draw_add: UserDrawAdd) -> Optional[UserDraw]:
        for field, value in user_draw_add.model_dump(exclude_unset=True).items():
            setattr(user_draw, field, value)
        return user_draw



