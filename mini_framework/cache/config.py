from pydantic import Field

from mini_framework.design_patterns.singleton import singleton
from mini_framework.web.std_models.base_model import BaseViewModel


class RedisServerConfig(BaseViewModel):
    """
    Redis 服务器配置
    """
    host: str = Field(..., title="Host", description="Redis 服务器地址")
    startup_nodes: list = Field(None, title="Startup Nodes", description="Redis 集群启动节点")
    port: int = Field(6379, title="Port", description="Redis 服务器端口")
    password: str = Field(None, title="Password", description="Redis 服务器密码")
    max_connections: int = Field(10, title="Max Connections", description="Redis 最大连接数")


class RedisDBConfig(BaseViewModel):
    """
    Redis 数据库配置
    """
    db: int = Field(..., title="DB", description="Redis 数据库")
    prefix: str = Field(..., title="Prefix", description="Redis Key 前缀")
    server_key: str = Field(..., title="Server Key", description="Redis 服务器 Key")
    server: RedisServerConfig = Field(..., title="Server", description="Redis 服务器配置")


@singleton
class RedisConfig:
    """
    Redis 配置
    """

    def __init__(self):
        """
        初始化 Redis 配置
        """
        from mini_framework.configurations import config_injection
        manager = config_injection.get_config_manager()
        cache_items = manager.get_domain_config('redis')
        if not cache_items:
            raise ValueError('redis config not found')
        server_configs = cache_items.get('servers')
        if not server_configs:
            raise ValueError('redis server config not found')
        self.__servers = {key: RedisServerConfig(**server_config) for key, server_config in server_configs.items()}
        db_configs = cache_items.get('dbs')
        if not db_configs:
            raise ValueError('redis db config not found')
        self.__dbs = {}
        for key, db_config in db_configs.items():
            server_key = db_config.get('server_key')
            db_config['server'] = self.__servers[server_key]
            self.__dbs[key] = RedisDBConfig(**db_config)

    @property
    def servers(self) -> dict[str, RedisServerConfig]:
        return self.__servers

    @property
    def dbs(self) -> dict[str, RedisDBConfig]:
        return self.__dbs


redis_config = RedisConfig()
