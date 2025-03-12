from mini_framework.cache.clients.client import AbstractRedisClient
from mini_framework.cache.clients.redis_client import RedisClient, RedisConnectionPool
from mini_framework.cache.clients.redis_cluster_client import RedisClusterPoolConnection, RedisClusterClient
from mini_framework.cache.config import redis_config
from mini_framework.design_patterns.singleton import singleton


@singleton
class RedisClientManager:
    """
    Redis 客户端管理器
    """

    def __init__(self):
        self.__config = redis_config
        self.__pools = {}

    def get_client(self, db_key: str) -> AbstractRedisClient:
        """
        获取 Redis 客户端
        :param db_key: Redis 数据库 Key
        :return:
        """
        db_config = self.__config.dbs.get(db_key, None)
        if not db_config:
            raise ValueError(f"Redis db config not found: {db_key}")
        pool = self.__pools.get(db_config.server_key, None)
        cluster = db_config.server.startup_nodes is not None
        if not pool:
            if cluster:
                pool = RedisClusterPoolConnection(db_config.server_key)
            else:
                pool = RedisConnectionPool(db_config.server_key)
            self.__pools[db_config.server_key] = pool
        if cluster:
            client = RedisClusterClient(pool=pool.pool, db=db_config.db, server_config=db_config.server)
        else:
            client = RedisClient(pool=pool.pool, db=db_config.db, server_config=db_config.server)
        return client


redis_client_manager = RedisClientManager()
