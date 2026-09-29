import redis
import json
from typing import Any, Union, List, Dict, Optional, Tuple, Iterable

from tool.yaml_utils import get_app_config

redis_conf = get_app_config("redis_pulse_conf")


_pool = redis.ConnectionPool(
    host=redis_conf['host'],
    port=redis_conf['port'],
    max_connections=redis_conf['max_connections'],
    decode_responses=redis_conf['decode_responses']
)


class RedisUtils:

    def __init__(self):
        self.pool = _pool

    # def __enter__(self):
    #     """支持上下文管理器"""
    #     self._client = redis.Redis(connection_pool=self.pool)
    #     return self
    #
    # def __exit__(self, exc_type, exc_val, exc_tb):
    #     """退出上下文时关闭连接"""
    #     self._client.close()

    def get_client(self) -> redis.Redis:
        """
        获取 Redis 客户端实例

        :return: redis.Redis 实例
        """
        return redis.Redis(connection_pool=self.pool)

    # 基础键操作
    def exists(self, key: str) -> bool:
        """检查键是否存在"""
        client = self.get_client()
        return client.exists(key) > 0

    def delete(self, *keys: str) -> int:
        """删除一个或多个键，返回删除数量"""
        client = self.get_client()
        return client.delete(*keys)

    def expire(self, key: str, seconds: int) -> bool:
        """设置键过期时间（秒）"""
        client = self.get_client()
        return client.expire(key, seconds)

    def ttl(self, key: str) -> int:
        """获取键剩余生存时间（秒）"""
        client = self.get_client()
        return client.ttl(key)

    # 字符串操作
    def set(self, key: str, value: Any, ex: int = None) -> bool:
        """
        设置键值
        :param ex: 过期时间（秒）
        """
        client = self.get_client()
        if isinstance(value, (dict, list)):
            value = json.dumps(value)
        return client.set(key, value, ex=ex)

    def get(self, key: str, default: Any = None) -> Any:
        """获取键值（自动解析JSON）"""
        client = self.get_client()
        value = client.get(key)
        if value is None:
            return default

        try:
            return json.loads(value)
        except json.JSONDecodeError:
            return value

    def incr(self, key: str, amount: int = 1) -> int:
        """自增操作"""
        client = self.get_client()
        return client.incr(key, amount)

    # 原子自增并在 key 首次创建时设置过期时间(固定窗口计数, 避免并发丢计数 + TTL 被重置)
    _INCR_WITH_EXPIRE_SCRIPT = """
        local cur = redis.call('INCR', KEYS[1])
        if cur == 1 then
            redis.call('EXPIRE', KEYS[1], ARGV[1])
        end
        return cur
        """

    def incr_with_expire(self, key: str, ex: int = None) -> int:
        """
        原子自增, 且仅在 key 首次创建时设置过期时间
        :param key: 键名
        :param ex: 过期时间(秒)
        :return: 自增后的计数值
        """
        client = self.get_client()
        return int(client.eval(self._INCR_WITH_EXPIRE_SCRIPT, 1, key, ex or 0))

    # 哈希操作
    def hset(self, key: str, field: str, value: Any) -> int:
        """设置哈希字段值"""
        client = self.get_client()
        if isinstance(value, (dict, list)):
            value = json.dumps(value)
        return client.hset(key, field, value)

    def hget(self, key: str, field: str, default: Any = None) -> Any:
        """获取哈希字段值"""
        client = self.get_client()
        value = client.hget(key, field)
        if value is None:
            return default

        try:
            return json.loads(value)
        except json.JSONDecodeError:
            return value

    def hgetall(self, key: str) -> Dict[str, Any]:
        """获取整个哈希表"""
        client = self.get_client()
        data = client.hgetall(key)
        result = {}
        for k, v in data.items():
            try:
                result[k] = json.loads(v)
            except json.JSONDecodeError:
                result[k] = v
        return result

    # 列表操作
    def lpush(self, key: str, *values: Any) -> int:
        """从左侧插入列表元素"""
        client = self.get_client()
        serialized = [json.dumps(v) if isinstance(v, (dict, list)) else v for v in values]
        return client.lpush(key, *serialized)

    def rpush(self, key: str, *values: Any) -> int:
        """从右侧插入列表元素"""
        client = self.get_client()
        serialized = [json.dumps(v) if isinstance(v, (dict, list)) else v for v in values]
        return client.rpush(key, *serialized)

    def rpop(self, key: str, default: Any = None) -> Any:
        """从右侧弹出列表元素"""
        client = self.get_client()
        value = client.rpop(key)
        if value is None:
            return default

        try:
            return json.loads(value)
        except json.JSONDecodeError:
            return value

    def lpop(self, key: str, default: Any = None) -> Any:
        """从左侧弹出列表元素"""
        client = self.get_client()
        value = client.lpop(key)
        if value is None:
            return default

        try:
            return json.loads(value)
        except json.JSONDecodeError:
            return value

    def lrange(self, key: str, start: int = 0, end: int = -1) -> List[Any]:
        """获取列表范围元素"""
        client = self.get_client()
        values = client.lrange(key, start, end)
        result = []
        for v in values:
            try:
                result.append(json.loads(v))
            except json.JSONDecodeError:
                result.append(v)
        return result

    # 集合操作
    def sadd(self, key: str, *values: Any) -> int:
        """向集合添加元素"""
        client = self.get_client()
        serialized = [json.dumps(v) if isinstance(v, (dict, list)) else v for v in values]
        return client.sadd(key, *serialized)

    def smembers(self, key: str) -> List[Any]:
        """获取集合所有元素"""
        client = self.get_client()
        values = client.smembers(key)
        result = []
        for v in values:
            try:
                result.append(json.loads(v))
            except json.JSONDecodeError:
                result.append(v)
        return result

    def srem(self, key: str, *values: Any) -> Any:
        """删除集合操作"""
        client = self.get_client()
        value = client.srem(key, *values)
        return value

    # 有序集合操作
    def zadd(self, key: str, mapping: dict, *values: Any) -> int:
        """向集合添加元素"""
        client = self.get_client()
        return client.zadd(name=key, mapping=mapping, *values)

    def zrange(self, key: str, start: int, end: int, withscores: bool = False) -> Union[List[Any],
                                                                                        List[Dict[str, Any]]]:
        """获取集合所有元素"""
        client = self.get_client()
        values = client.zrange(name=key, start=start, end=end, withscores=withscores)
        result = []
        # 逻辑分离，复用解码函数
        if not withscores:
            return [self.decode_value(v) for v in values]  # 列表推导更简洁
        else:
            for member, score in values:
                # 专门处理分数
                decoded_member = self.decode_value(member)
                # 处理分数
                if isinstance(score, bytes):
                    score = float(score.decode('utf-8'))
                else:
                    score = float(score)
                result.append({
                    "value": decoded_member,
                    "score": score
                })
        return result

    def zrem(self, key: str, *values: Any) -> Any:
        """删除集合操作"""
        client = self.get_client()
        value = client.zrem(key, *values)
        return value

    # 发布订阅
    def publish(self, channel: str, message: Any) -> int:
        """发布消息到频道"""
        client = self.get_client()
        if isinstance(message, (dict, list)):
            message = json.dumps(message)
        return client.publish(channel, message)

    # 高级功能
    def pipeline(self, flag):
        """获取管道对象（支持事务）"""
        client = self.get_client()
        return client.pipeline(transaction=flag)

    def scan_iter(self, match: str = None, count: int = 10) -> Iterable[str]:
        """迭代键（替代keys命令）"""
        client = self.get_client()
        return client.scan_iter(match=match, count=count)

    # 删除哈希中的指定字段
    def delete_hash(self, key: str, field: str) -> int:
        """
        删除哈希中的指定字段
        :param key: 哈希键名
        :param field: 要删除的字段名
        :return: 被删除的字段数量（0表示字段不存在）
        """
        client = self.get_client()
        return client.hdel(key, field)

    # def hash_delete_multi(self, key: str, field: str) -> int:
    #     client = self.get_client()
    #     return client.hdel(key, field)

    # 工具方法
    def set_json(self, key: str, value: Any, ex: int = None) -> bool:
        """设置JSON格式数据"""

        if isinstance(value, dict):
            value = json.dumps(value)
        return self.set(key, value, ex=ex)

    def get_json(self, key: str, default: Any = None) -> Any:
        """获取JSON格式数据"""
        value = self.get(key)
        if value is None:
            return default
        try:
            if type(value) is dict:
                return value
            return json.loads(value)
        except json.JSONDecodeError:
            return default

    def decode_value(self, v):
        """解码单个值：自动处理bytes和尝试JSON解析"""
        if isinstance(v, bytes):
            v = v.decode('utf-8')
        try:
            return json.loads(v)
        except (json.JSONDecodeError, UnicodeDecodeError):
            return v

    def close(self):
        """关闭连接池（通常在程序结束时调用）"""
        self.pool.disconnect()


# 创建依赖函数
def get_redis_utils() -> RedisUtils:
    return RedisUtils()
