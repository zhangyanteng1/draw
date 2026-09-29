from sqlalchemy import Column, DateTime, Index, Integer, SmallInteger, String, Text, DECIMAL, text

from db.base import Base


class Prize(Base):
    __tablename__ = "prize"
    __table_args__ = (
        Index("idx_type", "prize_type"),
        Index("idx_status", "status"),
        Index("idx_prize_sku", "prize_sku"),
        {"comment": "奖品表"},
    )

    id = Column(Integer, primary_key=True, autoincrement=True, comment="奖品主键ID")
    prize_name = Column(String(200), nullable=False, comment="奖品名称")
    brand = Column(String(100), nullable=True, comment="品牌")
    prize_sku = Column(String(100), nullable=False, comment="奖品sku")
    prize_type = Column(SmallInteger, nullable=False, comment="奖品类型：1实物 2虚拟卡券 3现金红包 4其他")
    color = Column(String(100), nullable=True, comment="奖品颜色")
    image_url = Column(String(500), nullable=True, comment="主图")
    description = Column(Text, nullable=True, comment="奖品描述/兑换说明")
    cost_price = Column(DECIMAL(10, 2), nullable=True, comment="成本价")
    market_price = Column(DECIMAL(10, 2), nullable=True, comment="市场价")
    total_stock = Column(Integer, nullable=False, server_default=text("0"), comment="总库存")
    remaining_stock = Column(Integer, nullable=False, server_default=text("0"), comment="剩余库存")
    status = Column(SmallInteger, nullable=False, server_default=text("1"), comment="状态：1上架 2下架")
    op_id = Column(Integer, nullable=True, comment="创建人user_id")
    up_id = Column(Integer, nullable=True, comment="更新人user_id")
    created_time = Column(DateTime, nullable=False, server_default=text("CURRENT_TIMESTAMP(6)"), comment="创建时间")
    updated_time = Column(DateTime, nullable=False, server_default=text("CURRENT_TIMESTAMP(6) ON UPDATE "
                                                                        "CURRENT_TIMESTAMP(6)"), comment="更新时间")
