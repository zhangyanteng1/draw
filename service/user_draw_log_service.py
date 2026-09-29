from sqlalchemy.orm import Session

from dao.draw_dao import DrawDao
from dao.user_dao import UserDao
from dao.user_draw_log_dao import UserDrawLogDao
from exceptions.exceptions import BusinessError
from model.user_draw_log import UserDrawLog


class UserDrawLogService:

    @staticmethod
    def save_user_draw_log(db: Session, user_draw_log: UserDrawLog):
        user = UserDao.get_by_user_id(db, user_draw_log.user_id)
        if not user:
            raise BusinessError("用户不存在")

        draw = DrawDao.get_by_draw_id(db, user_draw_log.draw_id)

        if not draw or draw.status != 2:
            raise BusinessError("抽奖活动不存在或已下线")

        UserDrawLogDao.insert(db, user_draw_log)
        db.commit()

