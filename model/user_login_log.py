from sqlalchemy import BigInteger, Column, DateTime, Index, Integer, SmallInteger, String, text

from db.base import Base


class UserLoginLog(Base):
    __tablename__ = "user_login_log"
    __table_args__ = (
        Index("idx_user_id", "user_id"),
        Index("idx_login_time", "login_time"),
        {"comment": "用户登录日志表"},
    )

    id = Column(BigInteger, primary_key=True, autoincrement=True, comment="主键id")
    user_id = Column(BigInteger, nullable=False, comment="用户id")
    ip = Column(String(64), nullable=True, comment="登录IP")
    device_name = Column(String(100), nullable=True, comment="设备名称")
    device_type = Column(SmallInteger, nullable=True, comment="设备类型：1桌面端 2移动端 3平板")
    os = Column(String(50), nullable=True, comment="操作系统")
    login_time = Column(DateTime(6), nullable=False, server_default=text("CURRENT_TIMESTAMP(6)"), comment="登录时间")
