from sqlalchemy import BigInteger, Column, DateTime, Index, Integer, text, String, SmallInteger

from db.base import Base


class UserDrawLog(Base):
    __tablename__ = "user_draw_log"
    __table_args__ = (
        Index("idx_user_id", "user_id"),
        Index("idx_draw_id", "draw_id"),
        {"comment": "用户抽奖日志"},
    )

    id = Column(Integer, primary_key=True, autoincrement=True, comment="主键id")
    user_id = Column(BigInteger, nullable=False, comment="用户id")
    draw_id = Column(Integer, nullable=False, server_default=text("0"), comment="抽奖活动id")
    draw_time = Column(DateTime, nullable=False, server_default=text("CURRENT_TIMESTAMP(6)"), comment="抽奖时间")
    is_win = Column(SmallInteger, nullable=False, server_default=text("0"), comment="是否中奖：0-未中，1-中奖")
    prize_name = Column(String(100), nullable=False, default="", comment="密码")
    prize_sku = Column(String(100), nullable=False, default="", comment="密码")
