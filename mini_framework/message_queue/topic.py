import random

from .config import kafka_config
from ..message_queue.kafka_utils import KafkaUtils
from ..utils.json import JsonUtils
from ..utils.log import logger


def _topic_name_exists(topic_names: list[str], topic_list: list[str]):
    """
    判断topic是否存在
    :param topic_names: topic名称
    :param topic_list: topic列表
    :return:
    """
    for topic_name in topic_names:
        if topic_name not in topic_list:
            return False
    return True


class Topic:
    """
    提供对kafka topic的操作封装
    """

    def __init__(self, topic_names: list[str], group_id: str = None):
        """
        初始化topic
        :param topic_names: topic的名称
        """
        self.__kafka_utils = KafkaUtils()
        self.__group_id = group_id if group_id else kafka_config.group_id
        self.__auto_offset_reset = (
            kafka_config.auto_offset_reset
            if kafka_config.auto_offset_reset is not None
            else "earliest"
        )
        self.__max_poll_interval_ms = (
            kafka_config.max_poll_interval_ms
            if kafka_config.max_poll_interval_ms is not None
            else 300000
        )
        self.__topic_names = topic_names
        self.__producer = self.__kafka_utils.get_producer()
        self.__topic_list = []
        self.__num_partitions = 1
        self.__num_replication_factor = 1
        self.__started = False

    @property
    def topic_details(self):
        """
        获取topic详情
        :return:
        """
        self.init()
        return self.__topic_list

    def init(self):
        """
        初始化topic
        :return:
        """
        if self.__topic_list:
            return
        topic_list = self.__kafka_utils.list_topics()
        not_exists_topics = [
            topic for topic in self.__topic_names if topic not in topic_list
        ]
        if len(not_exists_topics) > 0:
            self.__kafka_utils.create_topics(
                not_exists_topics,
                num_partitions=1,
                replication_factor=self.__num_replication_factor,
            )
            self.__topic_list = self.__kafka_utils.list_topics()
        else:
            self.__topic_list = topic_list

    @property
    def group_id(self):
        """
        返回group_id
        :return:
        """
        return self.__group_id

    @property
    def topic_names(self):
        """
        返回topic的名称
        :return:
        """
        return self.__topic_names

    @property
    def partitions(self):
        """
        返回topic的分区数
        :return:
        """
        return self.__num_partitions

    @property
    def replication_factor(self):
        """
        返回topic的副本数
        :return:
        """
        return self.__num_replication_factor

    async def send(self, topic: str, value: dict):
        """
        发送消息到topic
        :param topic: topic名称
        :param value: 消息内容
        :return:
        """
        topic_details = self.topic_details
        if topic not in topic_details:
            raise ValueError(f"Topic {topic} not found")

        message = JsonUtils.dict_to_json_str(value).encode("utf-8")
        await self.start_producer()
        await self.__producer.send_and_wait(topic, message)
        await self.__producer.flush()
        logger.info(f"Sent message to topic {topic}: {message}")

    async def start_producer(self):
        if not self.__started:
            await self.__producer.start()
            self.__started = True

    async def send_batch(self, messages: dict[str, list[dict]]):
        """
        发送批量消息到topic
        :param messages: 消息内容, key为topic名称, value为消息列表
        :return:
        """
        topic_batches = {}
        for topic, values in messages.items():
            if topic not in self.topic_details:
                raise ValueError(f"Topic {topic} not found")
            batch = list()
            for value in values:
                message = JsonUtils.dict_to_json_str(value).encode("utf-8")
                batch.append(dict(timestamp=None, value=message, key=None))
            topic_batches[topic] = batch
        await self.start_producer()
        for topic, values in topic_batches:
            batch = self.__producer.create_batch()
            for value in values:
                batch.append(**value)
            partitions = await self.__producer.partitions_for(topic)
            partition = random.choice(tuple(partitions))
            await self.__producer.send_batch(batch, topic, partition=partition)
        await self.__producer.flush()
        logger.info(f"Sent batch messages to topics: {messages}")

    async def stream(self):
        """
        从topic中获取消息流
        :return:
        """
        consumer = self.__kafka_utils.get_consumer(
            self.__group_id,
            self.__topic_names,
            auto_offset_reset=self.__auto_offset_reset,
            max_poll_interval_ms=self.__max_poll_interval_ms,
        )
        await consumer.start()
        try:
            async for message in consumer:
                msg_value = message.value.decode("utf-8")
                logger.info(f"Received message: {msg_value}")
                message_dict = JsonUtils.json_str_to_dict(msg_value)
                yield message_dict
        finally:
            await consumer.stop()

    async def ack(self, task):
        """
        确认消息
        :param task: 消息内容
        :return:
        """
        await self.__kafka_utils.ack(task)
