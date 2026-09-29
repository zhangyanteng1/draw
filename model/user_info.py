from sqlalchemy import BigInteger, Column, DateTime, Index, Integer, String, Text, text

from db.base import Base


class UserInfo(Base):
    __tablename__ = "user_info"
    __table_args__ = (
        Index("idx_user_id", "user_id"),
        {"comment": "用户信息表"},
    )

    id = Column(Integer, primary_key=True, autoincrement=True, comment="主键id")
    real_name = Column(String(50), nullable=False, default="", comment="用户名称")
    avatar = Column(String(255), nullable=False, default="", comment="用户头像")
    sex = Column(Integer, nullable=True, server_default=text("0"), comment="性别:1代表男, 2代表女")
    address = Column(String(255), nullable=False, default="", comment="详细居住地址")
    phone = Column(String(255), nullable=False, default="", comment="手机号")
    email = Column(String(100), nullable=False, default="", comment="邮箱")
    wechat = Column(String(100), nullable=False, default="", comment="微信号")
    user_id = Column(BigInteger, nullable=False, comment="关联用户id")
    desc = Column(Text, nullable=True, comment="个人简介")
    created_time = Column(DateTime, nullable=True, server_default=text("CURRENT_TIMESTAMP(6)"), comment="创建时间")
    updated_time = Column(DateTime, nullable=True, server_default=text("CURRENT_TIMESTAMP(6) ON UPDATE CURRENT_TIMESTAMP(6)"), comment="更新时间")
