import dataclasses

from mini_framework.context import env
from mini_framework.design_patterns.singleton import singleton

DEFAULT_DATABASE_KEY = "default"


@dataclasses.dataclass
class DatabaseConfig:
    """
    单个数据库实例配置, 配置项:
    * host: 数据库地址
    * port: 数据库端口
    * user: 数据库用户名
    * password: 数据库密码
    * database: 数据库名称
    * charset: 数据库编码
    * pool_size: 连接池大小
    * max_overflow: 最大溢出连接数
    * extra: 额外配置
    """

    master: bool
    async_driver: str
    sync_driver: str
    host: str
    port: int
    user: str
    password: str
    database: str
    charset: str = "utf8"
    pool_size: int = 5
    max_overflow: int = 10
    pool_timeout: int = 15
    pool_recycle = 3600
    pool_pre_ping = True
    extra: dict = None

    @property
    def async_database_uri(self):
        return f"{self.async_driver}://{self.user}:{self.password}@{self.host}:{self.port}/{self.database}"

    @property
    def sync_database_uri(self):
        return f"{self.sync_driver}://{self.user}:{self.password}@{self.host}:{self.port}/{self.database}"

    def __eq__(self, other):
        return (
            self.host == other.host
            and self.port == other.port
            and self.user == other.user
            and self.password == other.password
            and self.database == other.database
        )

    def __hash__(self):
        # example: hash(('localhost', 5432, 'postgres', '123123', 'test'))
        return hash(
            (
                self.host.lower(),
                self.port,
                self.user.lower(),
                self.password,
                self.database.lower(),
            )
        )


def remove_master_and_duplicates(master: DatabaseConfig, slaves: list[DatabaseConfig]):
    unique_slaves = []
    seen = set()
    for slave in slaves:
        if slave != master and slave not in seen:
            seen.add(slave)
            unique_slaves.append(slave)
    return unique_slaves


@dataclasses.dataclass
class DatabaseClusterConfig:
    """
    数据库集群配置
    """

    master: DatabaseConfig
    slaves: list[DatabaseConfig]
    sync_driver: str
    async_driver: str

    def __post_init__(self):
        """

        :return:
        """
        self.slaves = remove_master_and_duplicates(self.master, self.slaves)


@singleton
class DatabasesConfig:
    def __init__(self):
        self.__databases = None
        self.__invoke_type = None

    def __init_config(self):
        from mini_framework.configurations import config_injection

        manager = config_injection.get_config_manager()
        databases_dict = manager.get_domain_config("databases")
        if not databases_dict:
            return
        self.__invoke_type = env.sync_type
        self.__databases: dict[str, DatabaseClusterConfig] = {}
        for key, value in databases_dict.items():
            if value.get("master"):
                master_dict = value["master"]
                slaves_dict = value.get("slaves", [])
                sync_driver = value.get("sync_driver", "kingbase")
                async_driver = value.get("async_driver", "kingbase+asyncpg")
                master_dict["sync_driver"] = sync_driver
                master_dict["async_driver"] = async_driver
                master_dict["master"] = True
                master = DatabaseConfig(**master_dict)
                slaves = []
                for slave in slaves_dict:
                    slave["sync_driver"] = sync_driver
                    slave["async_driver"] = async_driver
                    slave["master"] = False
                    slaves.append(DatabaseConfig(**slave))
                self.__databases[key] = DatabaseClusterConfig(
                    master, slaves, sync_driver, async_driver
                )
            else:
                raise ValueError(
                    f"Database configuration section '{key}' must have a 'master' section."
                )

    def get_database(self, db_key: str) -> DatabaseClusterConfig:
        if not self.__databases:
            self.__init_config()
        if db_key not in self.__databases:
            raise KeyError(f"Database configuration section '{db_key}' not found.")
        return self.__databases.get(db_key)

    def get_master(self, db_key: str) -> DatabaseConfig:
        return self.get_database(db_key).master

    def get_slaves(self, db_key: str) -> list[DatabaseConfig]:
        return self.get_database(db_key).slaves

    @property
    def databases(self):
        if not self.__databases:
            self.__init_config()
        return self.__databases

    @property
    def master(self) -> DatabaseConfig:
        return self.get_database(DEFAULT_DATABASE_KEY).master

    @property
    def slaves(self) -> list[DatabaseConfig]:
        return self.get_database(DEFAULT_DATABASE_KEY).slaves

    def __getitem__(self, item: str) -> DatabaseClusterConfig:
        if not self.__databases:
            self.__init_config()
        return self.__databases[item]

    def __setitem__(self, key: str, value: DatabaseClusterConfig):
        raise NotImplementedError


db_config: DatabasesConfig = DatabasesConfig()

"""
Mock data:
{
    "databases": {
        "default": {
            "driver": "postgresql+psycopg2",
            "master": {
                "host": "localhost",
                "port": 5432,
                "user": "postgres",
                "password": "123456",
                "database": "master_db"
            },
            "slaves": [
                {
                    "host": "localhost",
                    "port": 5432,
                    "user": "postgres",
                    "password": "123456",
                    "database": "slave_db1"
                },
                {
                    "host": "localhost",
                    "port": 5432,
                    "user": "postgres",
                    "password": "123456",
                    "database": "slave_db2"
                }
            ]
        }
    }
}
"""
