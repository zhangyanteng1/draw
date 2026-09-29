import logging

from const.script_cache_key import ScriptCacheKey
from tool.redis_utils import RedisUtils

logger = logging.getLogger(__name__)


class ScriptCache:

    def __init__(self):
        self.redis_utils = RedisUtils()

    def acquire_task_lock(self, key: str, ex: int = 600) -> bool:
        """原子加锁，成功返回 True，已被锁定返回 False"""
        if not key:
            return False
        try:
            result = self.redis_utils.get_client().set(
                ScriptCacheKey.script_task_lock % key,
                key,
                nx=True,
                ex=ex
            )
            return result is not None
        except Exception as e:
            logger.error(f"acquire task lock error: {e}")
            return False

    def delete_task_lock(self, key: str) -> bool:
        if not key:
            return False
        try:
            self.redis_utils.delete(ScriptCacheKey.script_task_lock % key)
            return True
        except Exception as e:
            logger.error(f"delete task lock error: {e}")
            return False
