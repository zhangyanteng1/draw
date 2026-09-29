import logging
from typing import Optional

from tool.redis_utils import RedisUtils

logger = logging.getLogger(__name__)


class DrawCache:

    def __init__(self):
        self.redis_utils = RedisUtils()

    def acquire_user_draw_lock(self, key: str, ex: int = 600) -> bool:
        """原子加锁，成功返回 True，已被锁定返回 False"""
        if not key:
            return False
        try:
            result = self.redis_utils.get_client().set(
                key,
                key,
                nx=True,
                ex=ex
            )
            return result is not None
        except Exception as e:
            logger.error(f"acquire user draw lock error: {e}")
            return False

    def delete_user_draw_lock(self, key: str) -> bool:
        if not key:
            return False
        try:
            self.redis_utils.delete(key)
            return True
        except Exception as e:
            logger.error(f"delete user draw lock error: {e}")
            return False

    # 奖品库存预占: key 缺失时用 DB 可用值自愈初始化, 再原子检查并扣减
    _RESERVE_STOCK_SCRIPT = """
        if redis.call('EXISTS', KEYS[1]) == 0 then
            redis.call('SET', KEYS[1], ARGV[1])
        end
        local cur = tonumber(redis.call('GET', KEYS[1]))
        if cur and cur > 0 then
            redis.call('DECR', KEYS[1])
            return 1
        end
        return 0
        """

    def init_stock(self, key: str, value: int, ex: int = None) -> bool:
        """初始化奖品库存(仅当 key 不存在时设置, 幂等)"""
        if not key:
            return False
        try:
            client = self.redis_utils.get_client()
            result = client.set(key, value, nx=True, ex=ex)
            return result is not None
        except Exception as e:
            logger.error(f"init draw prize stock error: {e}")
            return False

    def reserve_stock(self, key: str, fallback_value: int) -> bool:
        """原子预占一份库存; key 缺失时用 fallback_value 自愈初始化。成功返回 True, 库存不足返回 False"""
        if not key:
            return False
        try:
            client = self.redis_utils.get_client()
            result = client.eval(self._RESERVE_STOCK_SCRIPT, 1, key, fallback_value)
            return int(result) == 1
        except Exception as e:
            logger.error(f"reserve draw prize stock error: {e}")
            return False

    def release_stock(self, key: str) -> bool:
        """释放一份预占的库存(补偿回滚用)"""
        if not key:
            return False
        try:
            self.redis_utils.get_client().incr(key)
            return True
        except Exception as e:
            logger.error(f"release draw prize stock error: {e}")
            return False

    def get_stock(self, key: str) -> Optional[int]:
        """读取奖品库存计数器当前值; key 不存在返回 None"""
        if not key:
            return None
        try:
            value = self.redis_utils.get(key)
            return int(value) if value is not None else None
        except (TypeError, ValueError) as e:
            logger.error(f"get draw prize stock error: {e}")
            return None

    def delete_stock(self, key: str) -> bool:
        """删除奖品库存计数器(对账修复: 交自愈逻辑在下次抽奖时用 DB 权威值重建)"""
        if not key:
            return False
        try:
            self.redis_utils.delete(key)
            return True
        except Exception as e:
            logger.error(f"delete draw prize stock error: {e}")
            return False
