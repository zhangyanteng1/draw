from sqlalchemy import BigInteger, Column, DateTime, Index, Integer, text
from sqlalchemy import UniqueConstraint

from db.base import Base


class UserDraw(Base):
    __tablename__ = "user_draw"
    __table_args__ = (
        UniqueConstraint("user_id", "draw_id", name="uk_user_draw"),
        Index("idx_draw_id", "draw_id"),
        {"comment": "用户抽奖次数"},
    )

    id = Column(Integer, primary_key=True, autoincrement=True, comment="主键id")
    user_id = Column(BigInteger, nullable=False, comment="用户id")
    draw_id = Column(Integer, nullable=False, server_default=text("0"), comment="抽奖活动id")
    total_quota = Column(Integer, nullable=False, server_default=text("0"), comment="抽奖次数")
    used_times = Column(Integer, nullable=False, server_default=text("0"), comment="已使用次数")
    created_time = Column(DateTime, nullable=False, server_default=text("CURRENT_TIMESTAMP(6)"), comment="创建时间")
    updated_time = Column(DateTime, nullable=False, server_default=text("CURRENT_TIMESTAMP(6) ON UPDATE "
                                                                        "CURRENT_TIMESTAMP(6)"), comment="更新时间")
