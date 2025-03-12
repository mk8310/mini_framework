from redis.commands.core import Script

from mini_framework.cache.clients.client import (
    AbstractRedisConnectionPool,
    AbstractRedisClient,
)


class RedisClusterPoolConnection(AbstractRedisConnectionPool):
    """
    Redis 集群连接池
    """

    def _initialize(self):
        from rediscluster import RedisCluster

        self._pool = RedisCluster(
            host=self.config.host,
            port=self.config.port,
            startup_nodes=self.config.startup_nodes,
            max_connections=self.config.max_connections,
            password=self.config.password,
        )


class RedisClusterClient(AbstractRedisClient):
    """
    Redis 集群客户端
    """

    def _initialize(self):
        from rediscluster import RedisCluster

        self.__client: RedisCluster = self.pool

    def register_script(self, script) -> Script:
        return self.__client.register_script(script)

    def connect(self):
        pass

    def disconnect(self):
        pass

    def __get_key(self, key):
        return f"{self.db}:{key}"

    def set(self, key, value, ex=None, px=None, nx=False, xx=False):
        key = self.__get_key(key)
        return self.__client.set(key, value, ex=ex, px=px, nx=nx, xx=xx)

    def get(self, key):
        key = self.__get_key(key)
        return self.__client.get(key)

    def delete(self, *keys):
        keys = [self.__get_key(key) for key in keys]
        return self.__client.delete(*keys)

    def exists(self, *keys):
        keys = [self.__get_key(key) for key in keys]
        return self.__client.exists(*keys)

    def expire(self, key, seconds):
        key = self.__get_key(key)
        return self.__client.expire(key, seconds)

    def expire_at(self, key, timestamp):
        key = self.__get_key(key)
        return self.__client.expireat(key, timestamp)

    def ttl(self, key):
        key = self.__get_key(key)
        return self.__client.ttl(key)

    def incr(self, key, amount=1):
        key = self.__get_key(key)
        return self.__client.incr(key, amount)

    def decr(self, key, amount=1):
        key = self.__get_key(key)
        return self.__client.decr(key, amount)

    def hset(self, name, key, value):
        key = self.__get_key(key)
        return self.__client.hset(name, key, value)

    def hget(self, name, key):
        key = self.__get_key(key)
        return self.__client.hget(name, key)

    def hdel(self, name, *keys):
        keys = [self.__get_key(key) for key in keys]
        return self.__client.hdel(name, *keys)

    def hkeys(self, name):
        name = self.__get_key(name)
        return self.__client.hkeys(name)

    def hincrby(self, name, key, amount=1):
        key = self.__get_key(key)
        return self.__client.hincrby(name, key, amount)

    def hexists(self, name, key):
        key = self.__get_key(key)
        return self.__client.hexists(name, key)

    def hlen(self, name) -> int:
        name = self.__get_key(name)
        return self.__client.hlen(name)

    def hget_all(self, name):
        name = self.__get_key(name)
        return self.__client.hgetall(name)

    def left_push(self, name, *values):
        name = self.__get_key(name)
        return self.__client.lpush(name, *values)

    def right_push(self, name, *values):
        name = self.__get_key(name)
        return self.__client.rpush(name, *values)

    def left_range(self, name, start, end):
        name = self.__get_key(name)
        return self.__client.lrange(name, start, end)

    def sadd(self, name, *values):
        name = self.__get_key(name)
        return self.__client.sadd(name, *values)

    def smembers(self, name):
        name = self.__get_key(name)
        return self.__client.smembers(name)

    def srem(self, name, *values):
        name = self.__get_key(name)
        return self.__client.srem(name, *values)

    def hmget(self, name, mapping) -> list:
        name = self.__get_key(name)
        return self.__client.hmget(name, mapping)

    def hmset(self, name, mapping) -> int:
        name = self.__get_key(name)
        return self.__client.hset(name, mapping=mapping)
