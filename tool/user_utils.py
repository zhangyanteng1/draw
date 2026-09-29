import logging
from typing import Optional

from argon2 import PasswordHasher

# 初始化 PasswordHasher
from argon2.exceptions import VerificationError, InvalidHash

from tool.uuid_utils import UUIDUtils

logger = logging.getLogger(__name__)


class UserUtils:

    ph = PasswordHasher(
        time_cost=2,  # 迭代次数
        memory_cost=19 * 1024,  # 内存使用（KiB），19 MiB
        parallelism=1,  # 并行线程数
        hash_len=16,  # 输出哈希长度
        salt_len=16  # 盐长度
    )

    @classmethod
    def hash_password_argon2(cls, plain_password: str) -> str:
        """
        使用 Argon2id 哈希密码
        """
        return cls.ph.hash(plain_password)

    @classmethod
    def verify_password_argon2(cls, plain_password: str, hashed_password: str) -> bool:
        """
        验证密码
        """
        try:
            cls.ph.verify(hashed_password, plain_password)
            return True
        except (VerificationError, InvalidHash):
            return False

    @classmethod
    def generate_user_id(cls) -> Optional[int]:
        """
        生成user_id
        """
        try:
            return UUIDUtils.get_uuid()
        except RuntimeError as e:
            logger.error(f"生成user_id出错: {e}")
            return None


# if __name__ == '__main__':
#     print(UserUtils.verify_password_argon2("1234567", "$argon2id$v=19$m=19456,t=2,p=1$5mJzaQFXOtAs9iValDKrAQ$alEJfYFEcYW5cGf4J5W02w"))
