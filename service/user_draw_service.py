import logging
from typing import Optional
from sqlalchemy.orm import Session

from dao.draw_dao import DrawDao
from dao.user_dao import UserDao
from dao.user_draw_dao import UserDrawDao
from exceptions.exceptions import BusinessError
from schema.user_draw_schema import UserDrawFilter, UserDrawAdd, UserDrawListResponse, UserDrawResponse, \
    DrawQualification


logger = logging.getLogger(__name__)


class UserDrawService:

    @staticmethod
    def save_or_update_user_draw(db: Session, user_draw_add: UserDrawAdd, user_id: int = None):

        # 鉴权注入的 user_id 优先, 兼容前端显式传参
        final_user_id = user_draw_add.user_id or user_id
        UserDrawService.check_user_draw(db, user_draw_add.draw_id, final_user_id)

        # 用最终的 user_id 查询(修复: 原代码误用 user_draw_add.user_id, 鉴权场景下恒为 None)
        user_draw_filter = UserDrawFilter(
            user_id=final_user_id,
            draw_id=user_draw_add.draw_id
        )
        user_draw = UserDrawDao.get_by_user_draw(db, user_draw_filter)

        try:
            if user_draw:
                # 已存在: 累加抽奖次数(不修改入参对象)
                update_data = UserDrawAdd(
                    user_id=user_draw.user_id,
                    draw_id=user_draw.draw_id,
                    total_quota=user_draw.total_quota + user_draw_add.total_quota,
                )
                UserDrawDao.update(db, user_draw, update_data)
            else:
                # 不存在: 新建记录
                insert_data = UserDrawAdd(
                    user_id=final_user_id,
                    draw_id=user_draw_add.draw_id,
                    total_quota=user_draw_add.total_quota,
                    used_times=user_draw_add.used_times,
                )
                UserDrawDao.insert(db, insert_data)
            # 事务由 service 统一收口
            db.commit()
        except Exception:
            db.rollback()
            raise

    @staticmethod
    def check_user_draw(db: Session, draw_id: int, user_id: int) -> Optional[bool]:

        if user_id:
            user = UserDao.get_by_user_id(db, user_id)

            if not user:
                raise BusinessError("用户不存在")

        if not draw_id:
            raise BusinessError("活动id为空")

        draw = DrawDao.get_by_draw_id(db, draw_id)
        if not draw or draw.status != 2:
            raise BusinessError("抽奖活动不存在或已下线")

        return True

    @staticmethod
    def get_user_draw_list(db: Session, user_draw_filter: UserDrawFilter) -> Optional[UserDrawListResponse]:
        user_draw_list, total_count = UserDrawDao.query_user_draw_list(db, user_draw_filter)

        user_draw_resp_list = [
            UserDrawResponse.model_validate(item) for item in user_draw_list
        ]

        # 构造最终响应
        response = UserDrawListResponse(
            total=total_count,
            list=user_draw_resp_list
        )

        return response

    @staticmethod
    def get_draw_qualification(db: Session, user_draw_filter: UserDrawFilter) -> DrawQualification:

        if not user_draw_filter.draw_id:
            raise BusinessError("抽奖活动id为空")

        draw = DrawDao.get_by_draw_id(db, user_draw_filter.draw_id)

        if not draw or draw.status != 2:
            raise BusinessError("抽奖活动不存在或已下线")

        user_draw = UserDrawDao.get_by_user_draw(db, user_draw_filter)

        if user_draw:
            draw_qualification = DrawQualification(
                is_draw=True,
                draw_number=user_draw.total_quota - user_draw.used_times
            )
            return draw_qualification

        return DrawQualification()
