from mini_framework.design_patterns.singleton import singleton


class TopicConfig:
    """
    从配置文件中读取kafka的topic的配置信息
    """

    def __init__(self, name: str, topic_config: dict):
        self.__topic_name = name
        self.__partitions = topic_config.get("partitions")
        self.__replication_factor = topic_config.get("replication_factor")

    @property
    def topic_name(self):
        """
        返回topic的名称
        :return:
        """
        return self.__topic_name

    @property
    def num_partitions(self):
        """
        返回topic的分区数
        :return:
        """
        return self.__partitions

    @property
    def num_replication_factor(self):
        """
        返回topic的副本数
        :return:
        """
        return self.__replication_factor


class BootstrapServer:
    """
    从配置文件中读取kafka的bootstrap server的配置信息
    """

    def __init__(self, server, port):
        self.__server = server
        self.__port = port

    @property
    def server(self):
        """
        返回server的地址
        :return:
        """
        return self.__server

    @property
    def port(self):
        """
        返回server的端口
        :return:
        """
        return self.__port

    def __str__(self):
        return f"{self.__server}:{self.__port}"


@singleton
class KafkaConfig:
    """
    从配置文件中读取kafka的配置信息
    """

    def __init__(self):
        from mini_framework.configurations import config_injection

        manager = config_injection.get_config_manager()
        kafka_dict = manager.get_domain_config("kafka")
        if not kafka_dict:
            return
        bootstrap_servers = kafka_dict.get("bootstrap_servers")
        self.__bootstrap_servers = []
        if bootstrap_servers:
            for server in bootstrap_servers:
                host = server.split(":")[0]
                port = server.split(":")[1]
                self.__bootstrap_servers.append(BootstrapServer(host, port))
        self.__auto_offset_reset = kafka_dict.get("auto_offset_reset", "earliest")
        self.__max_poll_interval_ms = kafka_dict.get("max_poll_interval_ms", 300000)
        self.__group_id = (
            kafka_dict.get("group_id") if "group_id" in kafka_dict.keys() else None
        )
        if self.__group_id is None:
            raise ValueError("group_id is required in kafka configuration")
        self.__topics = {}
        topics = kafka_dict.get("topics", {})
        for topic_name, topic_config in topics.items():
            self.__topics[topic_name] = TopicConfig(topic_name, topic_config)

    @property
    def bootstrap_servers(self) -> list[str]:
        """
        返回所有的bootstrap servers，格式为：["server:port", "server:port"]
        :return:
        """
        return [str(server) for server in self.__bootstrap_servers]

    @property
    def group_id(self) -> str:
        """
        返回group id
        :return:
        """
        return self.__group_id

    @property
    def auto_offset_reset(self) -> str:
        """
        返回auto offset reset的值, 默认为earliest
        :return:
        """
        return self.__auto_offset_reset

    @property
    def max_poll_interval_ms(self) -> int:
        """
        返回max poll interval ms的值, 默认为300000
        :return:
        """
        return self.__max_poll_interval_ms

    @property
    def topics(self):
        return self.__topics


kafka_config = KafkaConfig()

"""
{
    "kafka": {
        "bootstrap_servers": [
            "localhost:9092"
        ],
        "auto_offset_reset": "earliest",
        "max_poll_interval_ms": 300000,
        "group_id": "task-service",
        "topics": {
            "topic_name": {
                "name": "topic_name",
                "partitions": 1,
                "replication_factor": 1
            },
            "topic_name_2": {
                "name": "topic_name_2",
                "partitions": 1,
                "replication_factor": 1
            },
            "topic_name_3": {
                "name": "topic_name_3",
                "partitions": 1,
                "replication_factor": 1
            }
        }
    }
}
"""
