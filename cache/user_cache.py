import hashlib
import logging
from typing import Optional

from const.user_cache_key import UserCacheKey
from tool.redis_utils import RedisUtils


logger = logging.getLogger(__name__)


class UserCache:

    def __init__(self):
        self.redis_utils = RedisUtils()

    def set_refresh_token(self, user_id: int, refresh_token: str) -> bool:
        if not user_id or not refresh_token:
            return False
        try:
            self.redis_utils.set(key=UserCacheKey.REFRESH_TOKEN % user_id, value=refresh_token)
            return True
        except Exception as e:
            logger.error(f"set refresh token error: {e}")
            return False

    def get_refresh_token(self, user_id: int) -> Optional[str]:
        if not user_id:
            return None
        try:
            return self.redis_utils.get(key=UserCacheKey.REFRESH_TOKEN % user_id)
        except Exception as e:
            logger.error(f"get refresh token error: {e}")
            return None

    def delete_refresh_token(self, user_id: int) -> bool:
        if not user_id:
            return False
        try:
            self.redis_utils.delete(UserCacheKey.REFRESH_TOKEN % user_id)
            return True
        except Exception as e:
            logger.error(f"delete refresh token error: {e}")
            return False

    def set_login_error(self, key: str) -> bool:
        if not key:
            return False
        try:
            # 原子自增 + 首次创建时设置过期时间(Lua 脚本打包, 避免并发丢计数与 TTL 重置)
            self.redis_utils.incr_with_expire(key, UserCacheKey.USER_LOGIN_ERROR_EXPIRE)
            return True
        except Exception as e:
            logger.error(f"set login error: {e}")
            return False

    def get_login_error(self, key: str) -> Optional[int]:
        if not key:
            return None
        try:
            number = self.redis_utils.get(key)
            if number is None:
                return 0
            return number
        except Exception as e:
            logger.error(f"get login error: {e}")
            return 0

    def set_blacklist_token(self, access_token: str, ttl: int) -> bool:
        if not access_token or ttl <= 0:
            return False
        try:
            token_hash = hashlib.sha256(access_token.encode()).hexdigest()
            self.redis_utils.set(UserCacheKey.TOKEN_BLACKLIST % token_hash, 1, ttl)
            return True
        except Exception as e:
            logger.error(f"set blacklist token error: {e}")
            return False

    def is_blacklist_token(self, access_token: str) -> bool:
        if not access_token:
            return False
        try:
            token_hash = hashlib.sha256(access_token.encode()).hexdigest()
            return self.redis_utils.get(UserCacheKey.TOKEN_BLACKLIST % token_hash) is not None
        except Exception as e:
            logger.error(f"is blacklist token error: {e}")
            return False

