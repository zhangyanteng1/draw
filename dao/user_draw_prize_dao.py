from sqlalchemy.orm import Session
from model.user_draw_prize import UserDrawPrize


class UserDrawPrizeDao:

    @staticmethod
    def insert(db: Session, user_draw_prize: UserDrawPrize) -> UserDrawPrize:
        db.add(user_draw_prize)
        db.flush()
        db.refresh(user_draw_prize)
        return user_draw_prize

    @staticmethod
    def query_user_draw_prize_list(db: Session,):
        pass
