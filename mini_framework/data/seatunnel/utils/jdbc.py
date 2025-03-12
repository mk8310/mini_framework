import os
from enum import Enum

import aiohttp
from aiohttp.client import ClientSession

from mini_framework.utils.log import logger


class DBType(str, Enum):
    mysql = "mysql"
    postgresql = "postgresql"
    oracle = "oracle"
    sqlserver = "sqlserver"
    da_meng = "dm"
    doris = "doris"
    sqlite = "sqlite"
    starrocks = "starrocks"
    presto = "presto"
    hive = "hive"
    phoenix = "phoenix"

    @staticmethod
    def to_list():
        return list(map(lambda c: c.value, DBType))


db_type_drivers_map = {
    DBType.mysql: "com.mysql.cj.jdbc.Driver	",
    DBType.postgresql: "org.postgresql.Driver",
    DBType.oracle: "oracle.jdbc.OracleDriver",
    DBType.sqlite: "org.sqlite.JDBC",
    DBType.sqlserver: "com.microsoft.sqlserver.jdbc.SQLServerDriver",
    DBType.da_meng: "dm.jdbc.driver.DmDriver",
    DBType.doris: "com.mysql.cj.jdbc.Driver",
    DBType.starrocks: "com.mysql.cj.jdbc.Driver",
    DBType.hive: "org.apache.hive.jdbc.HiveDriver",
    DBType.phoenix: "org.apache.phoenix.queryserver.client.Driver",
    DBType.presto: "com.facebook.presto.jdbc.PrestoDriver",
}

db_type_urls_map = {
    DBType.mysql: "jdbc:mysql://{host}:{port}/{database}",
    DBType.postgresql: "jdbc:postgresql://{host}:{port}/{database}?currentSchema={schema}",
    DBType.oracle: "jdbc:oracle:thin:@{host}:{port}/{database}",
    DBType.sqlite: "jdbc:sqlite:{database}",
    DBType.sqlserver: "jdbc:sqlserver://{host}:{port};DatabaseName={database}",
    DBType.da_meng: "jdbc:dm://{host}:{port}/{database}",
    DBType.doris: "jdbc:mysql://{host}:{port}/{database}",
    DBType.starrocks: "jdbc:mysql://{host}:{port}/{database}",
    DBType.hive: "jdbc:hive2://{host}:{port}/{database}",
    DBType.phoenix: "jdbc:phoenix:thin:url=http://{host}:{port};serialization=PROTOBUF",
    DBType.presto: "jdbc:presto://{host}:{port}/{catalog}/{schema}",
}

db_type_maven_map = {
    DBType.mysql: "mysql:mysql-connector-java:8.0.33",
    DBType.postgresql: "org.postgresql:postgresql:42.2.23",
    DBType.oracle: "com.oracle.database.jdbc:ojdbc8:",
    DBType.sqlite: "org.xerial:sqlite-jdbc:3.34.0",
    DBType.sqlserver: "com.microsoft.sqlserver:mssql-jdbc:9.2.1.jre8",
    DBType.da_meng: "com.dameng:dameng-jdbc:1.0.0",
    DBType.doris: "com.mysql.cj:mysql-connector-java:8.0.23",
    DBType.starrocks: "com.mysql.cj:mysql-connector-java:8.0.23",
    DBType.hive: "org.apache.hive:hive-jdbc:3.1.2",
    DBType.phoenix: "org.apache.phoenix:phoenix-queryserver-client:5.1.2-HBase-2.0",
}


class DriverDownloader:
    def __init__(self, maven_domain: str = None, plugin_paths: list[str] = None):
        """
        初始化 DriverDownloader
        :param maven_domain: maven 仓库域名
        :param plugin_paths: 插件路径列表
        """
        from mini_framework.data.config import data_process_config

        if not maven_domain:
            maven_domain = data_process_config.seatunnel.maven_domain

        if not plugin_paths:
            plugin_paths = data_process_config.seatunnel.plugin_paths

        if not maven_domain:
            raise ValueError(
                "maven_domain is required, either in the constructor or in the config item seatunnel.maven_domain"
            )

        if not plugin_paths:
            raise ValueError(
                "plugin_paths is required, either in the constructor or in the config item seatunnel.plugin_paths"
            )

        self.maven_domain = maven_domain.rstrip("/")
        self.plugin_paths = plugin_paths

    def get_maven_coordinate(self, db_type: DBType):
        """
        获取 Maven 坐标
        :param db_type: 数据库类型
        :return: group_id, artifact_id, version
        """
        maven_coordinate = db_type_maven_map.get(db_type)
        if not maven_coordinate:
            raise ValueError(f"Unsupported db_type: {db_type}")

        parts = maven_coordinate.split(":")
        if len(parts) != 3:
            raise ValueError(
                f"Invalid maven coordinate for db_type {db_type}: {maven_coordinate}"
            )

        group_id, artifact_id, version = parts
        if not version:
            raise ValueError(
                f"No version specified for db_type {db_type}. Cannot download driver."
            )

        return group_id, artifact_id, version

    def construct_download_url(self, group_id: str, artifact_id: str, version: str):
        """
        构造下载 URL
        :param group_id: 组 ID
        :param artifact_id: 构件 ID
        :param version: 版本
        :return: 下载 URL
        """
        group_id_path = group_id.replace(".", "/")
        jar_file_name = f"{artifact_id}-{version}.jar"
        return (
            f"{self.maven_domain}/{group_id_path}/{artifact_id}/{version}/{jar_file_name}",
            jar_file_name,
        )

    def driver_exists(self, jar_file_name: str):
        """
        检查驱动文件是否已存在于所有插件路径
        :param jar_file_name: Jar 文件名
        :return: 布尔值，表示是否存在
        """
        return all(
            os.path.exists(os.path.join(path, jar_file_name))
            for path in self.plugin_paths
        )

    async def fetch_jar_content(self, download_url: str):
        """
        异步获取 Jar 文件内容
        :param download_url: 下载 URL
        :return: Jar 文件的二进制内容
        """
        async with aiohttp.ClientSession() as session:
            async with session.get(download_url) as resp:
                if resp.status == 200:
                    return await resp.read()
                elif resp.status == 404:
                    raise FileNotFoundError(f"Jar file not found at {download_url}")
                else:
                    raise ConnectionError(
                        f"Failed to download jar file from {download_url}, status code {resp.status}"
                    )

    def save_jar_to_paths(self, jar_content: bytes, jar_file_name: str):
        """
        保存 Jar 文件到所有插件路径
        :param jar_content: Jar 文件的二进制内容
        :param jar_file_name: Jar 文件名
        """
        for plugin_path in self.plugin_paths:
            jar_file_path = os.path.join(plugin_path, jar_file_name)
            if not os.path.exists(jar_file_path):
                os.makedirs(plugin_path, exist_ok=True)
                with open(jar_file_path, "wb") as f:
                    f.write(jar_content)
                logger.info(f"Downloaded jar file to {jar_file_path}")
            else:
                logger.info(f"Jar file already exists at {jar_file_path}")

    async def download_driver(self, db_type: DBType):
        """
        下载数据库驱动
        :param db_type: 数据库类型
        """
        group_id, artifact_id, version = self.get_maven_coordinate(db_type)
        download_url, jar_file_name = self.construct_download_url(
            group_id, artifact_id, version
        )

        if self.driver_exists(jar_file_name):
            logger.info("Jar file already exists in all plugin paths")
            return

        jar_content = await self.fetch_jar_content(download_url)
        self.save_jar_to_paths(jar_content, jar_file_name)
