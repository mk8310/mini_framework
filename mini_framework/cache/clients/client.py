from __future__ import annotations

from abc import ABC, abstractmethod

from redis.commands.core import Script

from mini_framework.cache.config import RedisServerConfig, redis_config


class AbstractRedisConnectionPool(ABC):
    def __init__(self, server_key: str):
        self._server_key = server_key
        self._server_config = redis_config.servers.get(server_key, None)
        if not self._server_config:
            raise ValueError(f"Redis server config not found: {server_key}")
        self._pool = None
        self._initialize()

    @abstractmethod
    def _initialize(self):
        raise NotImplementedError

    @property
    def pool(self):
        return self._pool

    @property
    def server_key(self) -> str:
        """
        获取 Redis 服务器 Key
        :return:
        """
        return self._server_key

    @property
    def config(self) -> RedisServerConfig:
        """
        获取 Redis 服务器配置
        :return:
        """
        return self._server_config


class AbstractRedisClient(ABC):
    """
    Redis 客户端抽象类
    """

    def __init__(self, pool, db, server_config: RedisServerConfig):
        """
        初始化 Redis 客户端
        :param pool: Redis 连接池
        :param db: Redis 数据库
        :param server_config: Redis 服务器配置
        """
        self._pool = pool
        self._db = db
        self._client = None
        self.__server_config = server_config
        self._initialize()

    @abstractmethod
    def _initialize(self):
        """
        初始化 Redis 客户端
        """
        raise NotImplementedError

    @property
    def config(self) -> RedisServerConfig:
        """
        获取 Redis 服务器配置
        """
        return self.__server_config

    @property
    def client(self):
        """
        获取 Redis 客户端
        :return:
        """
        return self._client

    @property
    def pool(self):
        """
        获取 Redis 连接池
        :return:
        """
        return self._pool

    @property
    def db(self):
        """
        获取 Redis 数据库
        :return:
        """
        return self._db

    @abstractmethod
    def connect(self):
        """
        建立与 Redis 服务器的连接
        """
        pass

    @abstractmethod
    def disconnect(self):
        """
        关闭与 Redis 服务器的连接
        """
        pass

    @abstractmethod
    def set(self, key, value, ex=None, px=None, nx=False, xx=False) -> bool | None:
        """
        设置键值对

        :param key: 键
        :param value: 值
        :param ex: 过期时间（秒）
        :param px: 过期时间（毫秒）
        :param nx: 如果设置为 True，则只有在键不存在时才设置值
        :param xx: 如果设置为 True，则只有在键已存在时才设置值
        :return: 设置成功返回 True，否则返回 False
        """
        pass

    @abstractmethod
    def get(self, key) -> str | None:
        """
        获取指定键的值

        :param key: 键
        :return: 键对应的值，如果键不存在则返回 None
        """
        pass

    @abstractmethod
    def delete(self, *keys) -> int:
        """
        删除一个或多个键

        :param keys: 要删除的键
        :return: 成功删除的键的数量
        """
        pass

    @abstractmethod
    def exists(self, *keys) -> int:
        """
        检查一个或多个键是否存在

        :param keys: 要检查的键
        :return: 存在的键的数量
        """
        pass

    @abstractmethod
    def expire(self, key, seconds) -> bool:
        """
        为指定键设置过期时间（秒）

        :param key: 键
        :param seconds: 过期时间（秒）
        :return: 设置成功返回 True，否则返回 False
        """
        pass

    @abstractmethod
    def expire_at(self, key, timestamp) -> bool:
        """
        为指定键设置过期时间戳（秒）

        :param key: 键
        :param timestamp: 过期时间戳（秒）
        :return: 设置成功返回 True，否则返回 False
        """
        pass

    @abstractmethod
    def ttl(self, key) -> int | None:
        """
        获取指定键的剩余过期时间（秒）

        :param key: 键
        :return: 剩余过期时间（秒），如果键不存在或没有设置过期时间，则返回 None
        """
        pass

    @abstractmethod
    def incr(self, key, amount=1) -> int:
        """
        对指定键的值进行自增操作

        :param key: 键
        :param amount: 自增的数量，默认为 1
        :return: 自增后的值
        """
        pass

    @abstractmethod
    def decr(self, key, amount=1) -> int:
        """
        对指定键的值进行自减操作

        :param key: 键
        :param amount: 自减的数量，默认为 1
        :return: 自减后的值
        """
        pass

    @abstractmethod
    def hset(self, name, key, value) -> int:
        """
        在指定的哈希表中设置键值对

        :param name: 哈希表名称
        :param key: 键
        :param value: 值
        :return: 如果键不存在并成功设置，返回 1；如果键已存在且成功更新，返回 0
        """
        pass

    @abstractmethod
    def hget(self, name, key) -> str:
        """
        获取指定哈希表中指定键的值

        :param name: 哈希表名称
        :param key: 键
        :return: 键对应的值，如果键不存在则返回 None
        """
        pass

    @abstractmethod
    def hincrby(self, name, key, amount=1) -> int:
        """
        对指定哈希表中的指定键的值进行自增操作

        :param name: 哈希表名称
        :param key: 键
        :param amount: 步长，默认为 1
        :return: 自增后的值
        """
        pass

    @abstractmethod
    def hdel(self, name, *keys) -> int:
        """
        删除指定哈希表中的一个或多个键

        :param name: 哈希表名称
        :param keys: 要删除的一个或多个键
        :return: 成功删除的键的数量
        """
        pass

    @abstractmethod
    def hkeys(self, name) -> list:
        """
        获取指定哈希表中所有的键

        :param name: 哈希表名称
        :return: 包含所有键的列表
        """
        pass

    @abstractmethod
    def hexists(self, name, key) -> bool:
        """
        检查指定哈希表中是否存在指定键

        :param name: 哈希表名称
        :param key: 键
        :return: 如果键存在则返回 True，否则返回 False
        """
        pass

    @abstractmethod
    def hlen(self, name) -> int:
        """
        获取指定哈希表中键值对的数量

        :param name: 哈希表名称
        :return: 键值对的数量
        """
        pass

    @abstractmethod
    def hget_all(self, name) -> dict:
        """
        获取指定哈希表中所有的键值对

        :param name: 哈希表名称
        :return: 包含所有键值对的字典
        """
        pass

    @abstractmethod
    def left_push(self, name, *values) -> int:
        """
        将一个或多个值插入到列表的左端

        :param name: 列表名称
        :param values: 要插入的一个或多个值
        :return: 插入后列表的长度
        """
        pass

    @abstractmethod
    def right_push(self, name, *values) -> int:
        """
        将一个或多个值插入到列表的右端

        :param name: 列表名称
        :param values: 要插入的一个或多个值
        :return: 插入后列表的长度
        """
        pass

    @abstractmethod
    def left_range(self, name, start, end) -> list:
        """
        获取列表中指定范围内的元素

        :param name: 列表名称
        :param start: 起始索引（包含）
        :param end: 结束索引（包含）
        :return: 指定范围内的元素列表
        """
        pass

    @abstractmethod
    def sadd(self, name, *values) -> int:
        """
        将一个或多个成员添加到集合中

        :param name: 集合名称
        :param values: 要添加的一个或多个成员
        :return: 成功添加的成员数量
        """
        pass

    @abstractmethod
    def smembers(self, name) -> set:
        """
        返回集合中的所有成员

        :param name: 集合名称
        :return: 包含所有成员的集合
        """
        pass

    @abstractmethod
    def srem(self, name, *values) -> int:
        """
        移除集合中的一个或多个成员

        :param name: 集合名称
        :param values: 要移除的一个或多个成员
        :return: 成功移除的成员数量
        """
        pass

    @abstractmethod
    def hmget(self, name, mapping) -> list:
        """
        获取哈希表中一个或多个字段的值

        :param name: 哈希表名称
        :param mapping: 包含字段的字典
        :return: 包含字段值的字典
        """
        pass

    @abstractmethod
    def hmset(self, name, mapping) -> int:
        """
        设置哈希表中的多个字段

        :param name: 哈希表名称
        :param mapping: 包含字段值的字典
        :return: 设置成功返回 True，否则返回 False
        """
        pass

    @abstractmethod
    def register_script(self, script) -> Script:
        """
        注册 Lua 脚本

        :param script: Lua 脚本
        :return: 脚本的 SHA1 校验和
        """
        pass
