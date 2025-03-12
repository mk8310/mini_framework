from aiokafka import (
    AIOKafkaProducer as KafkaProducer,
    AIOKafkaConsumer as KafkaConsumer,
)
from typing import List, Literal

from kafka.admin import NewTopic, KafkaAdminClient
from typing_extensions import deprecated

from mini_framework.design_patterns.singleton import singleton
from mini_framework.utils.json import JsonUtils


@singleton
class KafkaUtils:
    def __init__(self):
        from ..message_queue.config import kafka_config

        self.__bootstrap_servers = kafka_config.bootstrap_servers
        self.__topic_configs: dict = kafka_config.topics

    def create_topics(
        self, topics: List[str], num_partitions: int, replication_factor: int = 3
    ):
        """
        创建topic
        :param topics: topic列表
        :param num_partitions:
        :param replication_factor:
        :return:
        """
        admin_client = KafkaAdminClient(bootstrap_servers=self.__bootstrap_servers)
        topic_list = []
        for topic in topics:
            if topic in self.__topic_configs:
                topic_config = self.__topic_configs[topic]
                num_partitions = topic_config.num_partitions
                replication_factor = topic_config.num_replication_factor
            topic_list.append(
                NewTopic(
                    topic,
                    num_partitions=num_partitions,
                    replication_factor=replication_factor,
                )
            )
        resp = admin_client.create_topics(new_topics=topic_list, validate_only=False)
        admin_client.close()
        return resp

    def delete_topics(self, topics: List[str]):
        """
        删除topic
        :param topics: topic列表
        :return:
        """
        admin_client = KafkaAdminClient(bootstrap_servers=self.__bootstrap_servers)
        resp = admin_client.delete_topics(topics)
        admin_client.close()
        return resp

    def list_topics(self):
        """
        获取topic列表
        :return: topic列表
        """
        admin_client = KafkaAdminClient(bootstrap_servers=self.__bootstrap_servers)
        resp = admin_client.list_topics()
        admin_client.close()
        return resp

    def describe_topics(self, topics: List[str]):
        """
        获取topic详情
        :param topics: topic列表
        :return:
        """
        admin_client = KafkaAdminClient(bootstrap_servers=self.__bootstrap_servers)
        resp = admin_client.describe_topics(topics)
        admin_client.close()
        return resp

    def get_producer(self) -> KafkaProducer:
        """
        获取Kafka生产者
        :return:
        """
        return KafkaProducer(bootstrap_servers=self.__bootstrap_servers)

    def get_consumer(
        self,
        group_id: str,
        topics: List[str],
        *,
        auto_offset_reset: str = "earliest",
        max_poll_interval_ms: int = 300000
    ) -> KafkaConsumer:
        """
        获取Kafka消费者
        :param group_id: 消息分组ID
        :param topics: 主题列表
        :param auto_offset_reset: 自动重置偏移量, 可选值: "earliest", "latest", "none"
        :param max_poll_interval_ms: 最大拉取间隔, 单位: 毫秒, 默认: 300000
        :return:
        """
        return KafkaConsumer(
            *topics,
            bootstrap_servers=self.__bootstrap_servers,
            group_id=group_id,
            auto_offset_reset=auto_offset_reset,
            max_poll_interval_ms=max_poll_interval_ms,
        )

    def get_admin_client(self) -> KafkaAdminClient:
        """
        获取Kafka管理客户端
        :return: Kafka管理客户端
        """
        return KafkaAdminClient(bootstrap_servers=self.__bootstrap_servers)

    async def ack(self, task):
        """
        确认消息
        :param task: 消息内容
        :return:
        """
        pass


def consume(
    topics: List[str],
    group_id: str,
    *,
    auto_offset_reset: Literal["earliest", "latest", "none"] = "earliest",
    max_poll_interval_ms: int = 300000
):
    """
    消费消息
    :param topics: 需要消费的主题清单
    :param group_id: 消费者组ID
    :return:
    """

    def decorator(func):
        async def wrapper(*args, **kwargs):
            consumer = KafkaUtils().get_consumer(
                group_id,
                topics,
                auto_offset_reset=auto_offset_reset,
                max_poll_interval_ms=max_poll_interval_ms,
            )
            async for msg in consumer:
                # 将消息内容转换为json对象
                msg_value = msg.value.decode("utf-8")
                msg_value = JsonUtils.json_str_to_dict(msg_value)
                await func(msg_value, *args, **kwargs)

        return wrapper

    return decorator


@deprecated("Use kafka_producer instead")
async def publish(topic: str, msg_value: dict):
    """
    发布消息
    :param msg_value: 消息内容
    :param topic: 主题
    :return:
    """
    # 将消息内容转换为json字符串
    msg_value = JsonUtils.dict_to_json_str(msg_value)

    producer = KafkaUtils().get_producer()
    msg_bytes_value = msg_value.encode("utf-8")
    await producer.send_and_wait(topic, msg_bytes_value)


@singleton
class KFKProducer:
    def __init__(self):
        self.__kafka_utils = KafkaUtils()
        self.__producer = None
        self.__started = False

    async def publish(self, topic: str, msg_value: dict):
        """
        发布消息
        :param msg_value: 消息内容
        :param topic: 主题
        :return:
        """

        # 将消息内容转换为json字符串
        msg_value = JsonUtils.dict_to_json_str(msg_value)

        if not self.__producer:
            self.__producer = self.__kafka_utils.get_producer()

        if not self.__started:
            await self.__producer.start()

        msg_bytes_value = msg_value.encode("utf-8")
        await self.__producer.send_and_wait(topic, msg_bytes_value)

    async def stop(self):
        """
        停止生产者
        :return:
        """
        if not self.__started:
            return
        if not self.__producer:
            return
        await self.__producer.flush()
        await self.__producer.stop()
        self.__started = False


kafka_producer = KFKProducer()
