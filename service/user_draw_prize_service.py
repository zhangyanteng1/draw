from sqlalchemy.orm import Session

from dao.draw_dao import DrawDao
from dao.draw_prize_dao import DrawPrizeDao
from dao.user_dao import UserDao
from dao.user_draw_log_dao import UserDrawLogDao
from dao.user_draw_prize_dao import UserDrawPrizeDao
from exceptions.exceptions import BusinessError
from model.user_draw_prize import UserDrawPrize


class UserDrawLogService:

    @staticmethod
    def save_user_draw_prize(db: Session, user_draw_prize: UserDrawPrize):
        user = UserDao.get_by_user_id(db, user_draw_prize.user_id)
        if not user:
            raise BusinessError("用户不存在")

        draw = DrawDao.get_by_draw_id(db, user_draw_prize.draw_id)

        if not draw or draw.status != 2:
            raise BusinessError("抽奖活动不存在或已下线")

        draw_prize = DrawPrizeDao.get_by_draw_prize(db, user_draw_prize.draw_id,
                                                    user_draw_prize.prize_sku)

        if not draw_prize:
            raise BusinessError("配置的奖品不存在")

        UserDrawPrizeDao.insert(db, user_draw_prize)
        db.commit()

