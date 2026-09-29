from sqlalchemy import Column, DateTime, Integer, SmallInteger, String, Text, text

from db.base import Base


class Draw(Base):
    __tablename__ = "draw"
    __table_args__ = {"comment": "抽奖活动", "mysql_auto_increment": 10000}

    id = Column(Integer, primary_key=True, autoincrement=True, comment="主键id")
    draw_name = Column(String(100), nullable=False, comment="抽奖名称")
    status = Column(SmallInteger, nullable=False, server_default=text("1"), comment="状态 1:未开始 2:进行中 3:已结束 4:已下线")
    start_time = Column(DateTime, nullable=True, comment="抽奖开始时间")
    offline_time = Column(DateTime, nullable=True, comment="抽奖下线时间")
    desc = Column(Text, nullable=True, comment="抽奖描述")
    op_id = Column(Integer, nullable=True, comment="创建人user_id")
    up_id = Column(Integer, nullable=True, comment="更新人user_id")
    created_time = Column(DateTime, nullable=False, server_default=text("CURRENT_TIMESTAMP(6)"), comment="创建时间")
    updated_time = Column(DateTime, nullable=False, server_default=text("CURRENT_TIMESTAMP(6) ON UPDATE "
                                                                        "CURRENT_TIMESTAMP(6)"), comment="更新时间")
