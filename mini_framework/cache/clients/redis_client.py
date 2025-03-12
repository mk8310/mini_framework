from __future__ import annotations

import redis
from redis.commands.core import Script
from mini_framework.cache.clients.client import AbstractRedisClient, AbstractRedisConnectionPool


class RedisConnectionPool(AbstractRedisConnectionPool):
    """
    Redis 连接池
    """

    def _initialize(self):
        self._pool = redis.ConnectionPool(
            host=self.config.host,
            port=self.config.port,
            password=self.config.password,
            decode_responses=True,
            max_connections=self.config.max_connections,
        )


class RedisClient(AbstractRedisClient):
    """
    Redis 客户端
    """

    def connect(self):
        pass

    def disconnect(self):
        pass

    def set(self, key, value, ex=None, px=None, nx=False, xx=False) -> bool | None:
        return self._client.set(key, value, ex=ex, px=px, nx=nx, xx=xx)

    def get(self, key) -> str | None:
        return self._client.get(key)

    def delete(self, *keys) -> int:
        return self._client.delete(*keys)

    def exists(self, *keys) -> int:
        return self._client.exists(*keys)

    def expire(self, key, seconds) -> bool:
        return self._client.expire(key, seconds)

    def expire_at(self, key, timestamp) -> bool:
        return self._client.expireat(key, timestamp)

    def ttl(self, key) -> int | None:
        return self._client.ttl(key)

    def incr(self, key, amount=1) -> int:
        return self._client.incr(key, amount)

    def decr(self, key, amount=1) -> int:
        return self._client.decr(key, amount)

    def hset(self, name, key, value) -> int:
        return self._client.hset(name, key, value)

    def hget(self, name, key) -> str:
        return self._client.hget(name, key)

    def hincrby(self, name, key, amount=1) -> int:
        return self._client.hincrby(name, key, amount)

    def hdel(self, name, *keys) -> int:
        return self._client.hdel(name, *keys)

    def hkeys(self, name) -> list:
        return self._client.hkeys(name)

    def hexists(self, name, key) -> bool:
        return self._client.hexists(name, key)

    def hlen(self, name) -> int:
        return self._client.hlen(name)

    def hget_all(self, name) -> dict:
        return self._client.hgetall(name)

    def left_push(self, name, *values) -> int:
        return self._client.lpush(name, *values)

    def right_push(self, name, *values) -> int:
        return self._client.rpush(name, *values)

    def left_range(self, name, start, end) -> list:
        return self._client.lrange(name, start, end)

    def sadd(self, name, *values) -> int:
        return self._client.sadd(name, *values)

    def smembers(self, name) -> set:
        return self._client.smembers(name)

    def srem(self, name, *values) -> int:
        return self._client.srem(name, *values)

    def hmget(self, name, mapping) -> list:
        return self._client.hmget(name, mapping)

    def hmset(self, name, mapping) -> int:
        return self._client.hset(name, mapping=mapping)

    def register_script(self, script) -> Script:
        return self._client.register_script(script)

    def _initialize(self):
        """
        初始化 Redis 客户端
        """
        self._client = redis.StrictRedis(
            connection_pool=self.pool,
            db=self.db,
            decode_responses=True,
        )
