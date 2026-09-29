from sqlalchemy import BigInteger, Column, DateTime, Index, SmallInteger, String, text

from db.base import Base


class Requirement(Base):
    __tablename__ = "requirement"
    __table_args__ = (
        Index("idx_req_id", "req_id"),
        {"comment": "需求表"},
    )

    id = Column(BigInteger, primary_key=True, autoincrement=True, comment="主键id")
    req_id = Column(String(100), nullable=False, unique=True, comment="需求id")
    req_name = Column(String(200), nullable=False, comment="需求名称")
    product_users = Column(String(500), nullable=True, comment="产品人员(user_id逗号分隔)")
    dev_users = Column(String(500), nullable=True, comment="开发人员(user_id逗号分隔)")
    test_users = Column(String(500), nullable=True, comment="测试人员(user_id逗号分隔)")
    dev_start_time = Column(DateTime, nullable=True, comment="研发开始时间")
    dev_end_time = Column(DateTime, nullable=True, comment="研发结束时间")
    test_start_time = Column(DateTime, nullable=True, comment="测试开始时间")
    test_end_time = Column(DateTime, nullable=True, comment="测试结束时间")
    online_time = Column(DateTime, nullable=True, comment="上线时间")
    skip_test = Column(SmallInteger, nullable=False, server_default=text("0"), comment="是否免测 0否 1是")
    requester = Column(String(100), nullable=True, comment="需求方")
    op_id = Column(BigInteger, nullable=True, comment="创建人user_id")
    up_id = Column(BigInteger, nullable=True, comment="更新人user_id")
    created_time = Column(DateTime, nullable=True, server_default=text("CURRENT_TIMESTAMP(6)"), comment="创建时间")
    updated_time = Column(DateTime, nullable=True, server_default=text("CURRENT_TIMESTAMP(6) ON UPDATE "
                                                                       "CURRENT_TIMESTAMP(6)"), comment="更新时间")
