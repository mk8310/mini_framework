from ..plugin import Plugin
from .data_sink import DataSink
from .data_source import DataSource
from ..utils.jdbc import (
    DBType,
    db_type_drivers_map,
    db_type_urls_map,
)


class JDBCPlugin(Plugin):
    """JDBC 源配置类"""

    def validate(self):
        if self.driver is None or self.driver == "":
            raise ValueError("driver 不能为空")
        if self.url is None or self.url == "":
            raise ValueError("url 不能为空")

    def __init__(
        self,
        db_type: DBType,
        query,
        host,
        port,
        database,
        schema,
        user=None,
        password=None,
        **kwargs,
    ):
        """
        初始化 JDBC 源配置
        :param db_type: 数据库类型
        :param host: 数据库主机
        :param port: 数据库端口
        :param database: 数据库名称
        :param schema: 数据库 schema
        :param query: 查询语句
        :param user: 数据库访问用户名
        :param password: 数据库访问密码
        :param kwargs: 其他配置项
        """
        if db_type not in DBType.to_list():
            raise ValueError(f"不支持的数据库类型 {db_type}")

        self._db_type = db_type

        driver = (
            db_type_drivers_map.get(db_type) if db_type in db_type_drivers_map else None
        )
        url_params = {"host": host, "port": port}
        if database:
            url_params["database"] = database
        if schema:
            url_params["schema"] = schema
        url = (
            db_type_urls_map.get(db_type).format(**url_params)
            if db_type in db_type_urls_map
            else None
        )
        super().__init__(
            plugin="jdbc",
            driver=driver,
            url=url,
            query=query,
            user=user,
            password=password,
            **kwargs,
        )
        self.driver = driver
        self.url = url
        self.query = query
        self.user = user
        self.host = host
        self.port = port
        self.database = database
        self.schema = schema
        self.password = password
        self.config = kwargs  # 其他配置项可通过kwargs传入

    @property
    def db_type(self):
        return self._db_type

    def to_plugin_dict(self):
        return {
            "driver": self.driver,
            "url": self.url,
            "query": self.query,
            "user": self.user,
            "password": self.password,
            **self.config,
        }


class JDBCSink(DataSink):
    def __init__(
        self,
        db_type: DBType,
        query,
        host,
        port,
        database,
        schema,
        user=None,
        password=None,
        source_table_name=None,
        parallelism=None,
        **kwargs,
    ):
        """
        初始化 JDBC Sink 配置
        :param db_type: 数据库类型
        :param query: 查询语句
        :param host: 数据库主机
        :param port: 数据库端口
        :param database: 数据库名称
        :param schema: 数据库 schema
        :param user: 数据库访问用户名
        :param password: 数据库访问密码
        :param source_table_name: 当不指定 source_table_name 时，当前插件处理配置文件中上一个插件输出的数据集 dataset; 当指定了 source_table_name 时，当前插件正在处理该参数对应的数据集
        :param parallelism: 当没有指定parallelism时，默认使用 env 中的 parallelism。当指定 parallelism 时，它将覆盖 env 中的 parallelism。
        :param kwargs: 其他配置项
        """
        jdbc_plugin = JDBCPlugin(
            db_type, query, host, port, database, schema, user, password, **kwargs
        )
        super().__init__(jdbc_plugin, source_table_name, parallelism)

    def to_plugin_dict(self):
        return self.to_dict()


class JDBCSource(DataSource):
    def __init__(
        self,
        db_type: DBType,
        query,
        host,
        port,
        database,
        schema,
        user=None,
        password=None,
        result_table_name=None,
        parallelism=None,
        **kwargs,
    ):
        """
        初始化 JDBC 源配置
        :param db_type: 数据库类型
        :param query: 查询语句
        :param host: 数据库主机
        :param port: 数据库端口
        :param database: 数据库名称
        :param schema: 数据库 schema
        :param user: 数据库访问用户名
        :param password: 数据库访问密码
        :param result_table_name: 当未指定 result_table_name 时，此插件处理的数据将不会被注册为可由其他插件直接访问的数据集 (dataStream/dataset)，或称为临时表 (table)。当指定了 result_table_name 时，此插件处理的数据将被注册为可由其他插件直接访问的数据集 (dataStream/dataset)，或称为临时表 (table)。此处注册的数据集 (dataStream/dataset) 可通过指定 source_table_name 直接被其他插件访问。
        :param parallelism: 当没有指定 parallelism 时，默认使用 env 中的 parallelism。当指定 parallelism 时，它将覆盖 env 中的 parallelism。
        :param kwargs:
        """
        jdbc_plugin = JDBCPlugin(
            db_type, query, host, port, database, schema, user, password, **kwargs
        )
        super().__init__(jdbc_plugin, result_table_name, parallelism)

    def to_plugin_dict(self):
        return self.to_dict()
