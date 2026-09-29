from sqlalchemy import BigInteger, Column, DateTime, Index, Integer, SmallInteger, String, text

from db.base import Base


class UserDrawPrize(Base):
    __tablename__ = "user_draw_prize"
    __table_args__ = (
        Index("idx_user_id", "user_id"),
        Index("idx_draw_id", "draw_id"),
        Index("idx_prize_id", "draw_prize_id"),
        Index("idx_prize_sku", "prize_sku"),
        {"comment": "用户获奖记录"},
    )

    id = Column(Integer, primary_key=True, autoincrement=True, comment="主键id")
    user_id = Column(BigInteger, nullable=False, comment="用户id")
    draw_id = Column(Integer, nullable=False, server_default=text("0"), comment="抽奖活动id")
    draw_prize_id = Column(Integer, nullable=False, server_default=text("0"), comment="奖品配置id")
    prize_sku = Column(String(100), nullable=False, server_default=text("''"), comment="奖品唯一标识")
    status = Column(SmallInteger, nullable=False, server_default=text("0"), comment="领奖状态 0:未领取 1:已领取 2:已过期")
    draw_time = Column(DateTime, nullable=False, server_default=text("CURRENT_TIMESTAMP(6)"), comment="抽奖时间")
    claim_time = Column(DateTime, nullable=True, comment="领取时间")
    expire_time = Column(DateTime, nullable=True, comment="过期时间")
