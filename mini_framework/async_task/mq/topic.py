from datetime import datetime
from typing import Union

import shortuuid

from ..config import task_service_config
from ..data_access.task_rule import TaskRule
from ..router import task_router
from ..task.task import BatchTasks, Task
from ...databases.conn_managers.utilities import database_transaction_id
from ...databases.entities.db_executor import db_transaction
from ...design_patterns.depend_inject import get_injector
from ...message_queue.topic import Topic
from ...utils.log import logger


class TaskTopic:
    """
    提供对kafka topic的操作封装
    """

    def __init__(self):
        self.__topic_names = task_router.task_type_topics
        self.__topic = Topic(self.__topic_names, group_id="task-service")

    @property
    def topic_names(self):
        """
        返回topic的名称
        :return:
        """
        return self.__topic_names

    async def send(self, task: Union[Task, BatchTasks], failure_retry: bool = False):
        """
        发送消息到topic
        :param task: 需要开启的任务上下文
        :param failure_retry: 是否失败重试
        :return:
        """
        if isinstance(task, BatchTasks):
            return await self.__batch_send(task, failure_retry)
        elif isinstance(task, Task):
            return await self.__send(task, failure_retry)
        else:
            raise ValueError("value must be Task or BatchTasks")

    async def __send(self, task: Task, failure_retry: bool = False):
        """
        发送单个消息到 topic
        :param task: 消息内容
        :param failure_retry: 是否失败重试
        :return:
        """
        task.task_id = shortuuid.uuid() if not task.task_id else task.task_id
        task.created_at = datetime.now() if not task.created_at else task.created_at
        task.app_id = task_service_config.app_id
        topic_name = task_router.get_task_type(task.task_type).topic
        task_data_processor = task_router.get_task_data_processor(task.task_type)
        message = task_data_processor.serialize_task(task)
        if not failure_retry:
            await self.__save_task(task)
        await self.__topic.send(topic_name, message)
        return task

    @db_transaction
    async def __save_task(self, task):
        task_rule: TaskRule = get_injector(TaskRule)
        await task_rule.create_task(task)

    async def __batch_send(self, batch_tasks: BatchTasks, failure_retry: bool = False):
        """
        发送批量消息到topic
        :param batch_tasks: 消息内容
        :return:
        """
        messages = dict()
        for task in batch_tasks.tasks:
            task.task_id = shortuuid.uuid() if not task.task_id else task.task_id
            task.app_id = task_service_config.app_id
            topic_name = task_router.get_task_type(task.task_type).topic
            if topic_name not in messages:
                messages[topic_name] = []
            task_data_processor = task_router.get_task_data_processor(task.task_type)
            messages[topic_name].append(task_data_processor.serialize_task(task))
            if not failure_retry:
                await self.__save_task(task)
        await self.__topic.send_batch(messages)
        return batch_tasks

    async def ack(self, task: Task):
        """
        确认消息
        :param task: 消息内容
        :return:
        """
        await self.__topic.ack(task)

    async def stream(self):
        """
        从topic中获取消息流
        :return:
        """
        async for message in self.__topic.stream():
            try:
                if "task_type" not in message.keys():
                    logger.error(f"Invalid message: {message}, missing task_type")
                    continue
                task_data_processor = task_router.get_task_data_processor(
                    message.get("task_type")
                )
                task = task_data_processor.deserialize_task(message)
            except Exception as e:
                logger.error(f"Failed to parse message: {message}, error: {e}")
                continue
            yield task
