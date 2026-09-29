from sqlalchemy import BigInteger, Column, DateTime, Index, Integer, String, text

from db.base import Base


class User(Base):
    __tablename__ = "user"
    __table_args__ = (
        Index("idx_user_id", "user_id", unique=True),
        {"comment": "用户表"},
    )

    id = Column(Integer, primary_key=True, autoincrement=True, comment="主键id")
    user_id = Column(BigInteger, nullable=False, comment="用户id")
    username = Column(String(50), nullable=False, unique=True, default="", comment="用户名")
    password = Column(String(255), nullable=False, default="", comment="密码")
    status = Column(Integer, nullable=False, server_default=text("1"), comment="类型:1代表正常, 2代表禁用, 3代表注销")
    created_time = Column(DateTime, nullable=True, server_default=text("CURRENT_TIMESTAMP(6)"), comment="创建时间")
    updated_time = Column(DateTime, nullable=True, server_default=text("CURRENT_TIMESTAMP(6) ON UPDATE "
                                                                              "CURRENT_TIMESTAMP(6)"), comment="更新时间")
