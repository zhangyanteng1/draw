from sqlalchemy import Column, DateTime, Index, Integer, SmallInteger, String, Text, text

from db.base import Base


class DrawPrize(Base):
    __tablename__ = "draw_prize"
    __table_args__ = (
        Index("idx_draw_id", "draw_id"),
        {"comment": "奖品配置"},
    )

    id = Column(Integer, primary_key=True, autoincrement=True, comment="主键id")
    draw_id = Column(Integer, nullable=False, server_default=text("0"), comment="抽奖活动id")
    prize_name = Column(String(100), nullable=False, comment="奖品名称")
    prize_sku = Column(String(100), nullable=False, server_default=text("''"), comment="奖品唯一标识")
    prize_type = Column(SmallInteger, nullable=False, server_default=text("0"), comment="奖品类型 1:实物 2:优惠券")
    is_guaranteed = Column(SmallInteger, nullable=False, server_default=text("0"), comment="是否兜底 0:否 1:是")
    prize_price = Column(Integer, nullable=False, server_default=text("0"), comment="奖品价格(分)")
    prize_inventory = Column(Integer, nullable=False, server_default=text("0"), comment="奖品库存")
    draw_prize_status = Column(SmallInteger, nullable=False, server_default=text("1"), comment="奖品状态 （1:上架，2:下架）")
    reduce_inventory = Column(Integer, nullable=False, server_default=text("0"), comment="已消耗库存")
    prize_picture = Column(Text, nullable=True, comment="奖品图片")
    probability = Column(Integer, nullable=False, server_default=text("0"), comment="奖品概率(万分比 0-10000)")
    op_id = Column(Integer, nullable=True, comment="创建人user_id")
    up_id = Column(Integer, nullable=True, comment="更新人user_id")
    created_time = Column(DateTime, nullable=False, server_default=text("CURRENT_TIMESTAMP(6)"), comment="创建时间")
    updated_time = Column(DateTime, nullable=False, server_default=text("CURRENT_TIMESTAMP(6) ON UPDATE "
                                                                        "CURRENT_TIMESTAMP(6)"), comment="更新时间")
