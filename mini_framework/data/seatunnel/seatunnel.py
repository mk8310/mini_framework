from .config import Config
from .job_env import JobEnvironment
from .plugins import DataSource, DataSink, JDBCSource, JDBCSink
from .plugins.jdbc import JDBCPlugin
from .transformers import Transformer


class SeatunnelConfig(Config):
    """Seatunnel 核心配置类"""

    def validate(self):
        if self.__env:
            self.__env.validate()
        for key, source in self.__sources.items():
            source.validate()
        for transformer in self.__transforms:
            transformer.validate()
            if transformer.source_table_name not in self.__sources.keys():
                raise ValueError(
                    f"source_table_name 在 source 配置中不存在: {transformer.source_table_name}"
                )
            if transformer.result_table_name not in self.__sinks.keys():
                raise ValueError(
                    f"result_table_name 在 sink 配置中不存在: {transformer.result_table_name}"
                )

        for key, sink in self.__sinks.items():
            sink.validate()

            if sink.source_table_name not in self.__sources.keys():
                raise ValueError(f"source_table_name 不存在: {sink.source_table_name}")

    def __init__(self):
        self.__sources: dict[str, DataSource] = dict()
        self.__transforms: list[Transformer] = []
        self.__sinks: dict[str, DataSink] = dict()
        self.__env: JobEnvironment = None

    def set_env(self, env: JobEnvironment):
        self.__env = env

    def add_source(self, source: DataSource):
        if source.result_table_name in self.__sources.keys():
            raise ValueError(f"source_table_name 重复: {source.result_table_name}")
        self.__sources[source.result_table_name] = source

    def add_transform(self, transformer: Transformer):
        self.__transforms.append(transformer)

    def add_sink(self, sink: DataSink):
        if sink.source_table_name in self.__sinks.keys():
            raise ValueError(f"source_table_name 重复: {sink.source_table_name}")
        self.__sinks[sink.source_table_name] = sink

    def _to_dict(self):
        """
        将配置转换为 dict 格式
        :return:
        """
        result = {
            "source": [source.to_dict() for source in self.__sources.values()],
            "transform": [transform.to_dict() for transform in self.__transforms],
            "sink": [sink.to_dict() for sink in self.__sinks.values()],
        }
        if self.__env:
            result["env"] = self.__env.to_dict()
        return result

    def to_json(self):
        """
        将配置转换为 json 格式
        :return:
        """
        import json

        return json.dumps(self._to_dict(), indent=2)

    def to_yaml(self):
        """
        将配置转换为 yaml 格式
        :return:
        """
        import yaml

        return yaml.dump(self._to_dict(), indent=2)

    def to_hocon(self):
        """
        将配置转换为 hocon 格式, seatunnel 配置文件默认使用 hocon 格式
        :return:
        """
        from pyhocon import ConfigFactory, HOCONConverter

        config = ConfigFactory.from_dict(self._to_dict())
        return HOCONConverter.to_hocon(config)

    def _download_all_drivers(self):
        """
        下载所有驱动
        :return:
        """
        db_types = []
        for source in self.__sources.values():
            if isinstance(source, JDBCSource) and isinstance(source.plugin, JDBCPlugin):
                db_types.append(source.plugin.db_type)

        for sink in self.__sinks.values():
            if isinstance(sink, JDBCSink) and isinstance(sink.plugin, JDBCPlugin):
                db_types.append(sink.plugin.db_type)

        db_types = list(set(db_types))
        from mini_framework.data.seatunnel.utils import DriverDownloader
        downloader = DriverDownloader(maven_domain="https://repo1.maven.org/maven2", plugin_paths=[])
        for db_type in db_types:
            downloader.download_driver(db_type)

    def save(self, path: str):
        """
        保存配置到文件
        :param path: 文件路径
        :return:
        """
        self._download_all_drivers()
        hocon_content = self.to_hocon()
        with open(path, "w") as f:
            f.write(hocon_content)
