from typing import Optional

import shortuuid
from cachetools import LRUCache

from .event_type import EventType
from .retry import NormalTaskRetry, TaskRetry
from .task_data_processor import TaskDataProcess
from ..event_bus import event_bus, get_event
from ..task.task_context import Context
from ...databases.entities.db_executor import db_transaction
from ...utils.log import logger
from ...web.std_models.errors import MiniHTTPException

_task_types_cache = LRUCache(maxsize=100)


class TaskConsumer:
    def __init__(self, app):
        """
        初始化任务消费者
        :param app: 应用程序
        """
        from ..app.app import TaskApplication

        self.__task_retry: Optional[TaskRetry] = NormalTaskRetry(self)
        self.__event_bus = event_bus
        self.__app: "TaskApplication" = app

    @property
    def app(self):
        return self.__app

    async def consume(self):
        """
        从 Kafka 消费任务消息
        :return:
        """
        task_topic = self.__app.task_topic
        if not task_topic:
            raise ValueError("No topic found for task")

        async for task in task_topic.stream():
            context_id = shortuuid.uuid()
            context = Context(task=task, context_id=context_id)
            from mini_framework.async_task.router import task_router

            task_data_processor = task_router.get_task_data_processor(task.task_type)

            task_data_processor.prepare(self)
            try:
                await self._publish_event(context, EventType.event)
                await self._execute_task(context, task_data_processor)
                await self._handle_success(context, task_data_processor)
                await self._publish_event(context, EventType.success)
                await self._execute_after_task(context, task_data_processor)
            except Exception as e:
                await self.handle_failure(context, e)
                await self._publish_event(context, EventType.failure, e)
            finally:
                await task_topic.ack(task)

    async def handle_failure(self, context, exception):
        """
        处理任务执行失败的情况。
        :param context: 失败的任务对象。
        :param exception: 引发的异常。
        """
        if isinstance(exception, MiniHTTPException):
            logger.error(f"Task execute failed: {exception}")
            return
        retried_task = await self.__task_retry.retry(context, exception)
        if retried_task:
            logger.error(f"Task failed and retry: {context.task.task_type}")
            await self.__app.task_topic.send(retried_task, failure_retry=True)
        else:
            logger.error(f"Task failed and retry also failed: {context.task.task_type}")

    def _publish_event(
        self, context, event_type: EventType = EventType.event, ex: Exception = None
    ):
        """
        发布事件
        :param context: 上下文
        :param event_type: 事件类型
        :param ex: 异常信息
        :return:
        """
        e = get_event(context, event_type=event_type, ex=ex)
        return self.__event_bus.publish(e)

    @db_transaction
    async def _execute_task(self, context: Context, task_data_process: TaskDataProcess):
        """
        执行任务
        :param context: 上下文
        :param task_data_process: 任务类型上下文
        :return:
        """
        if self.__app.context.before_executor:
            await self.__app.context.before_executor.execute(context)
        for before_exec in task_data_process.before_execs:
            await before_exec.execute(context)
        await task_data_process.executor.execute(context)

    @db_transaction
    async def _handle_success(
        self, context: Context, task_data_process: TaskDataProcess
    ):
        """
        处理成功
        :param context: 上下文
        :param task_data_process: 任务类型上下文
        :return:
        """
        if task_data_process.success_handler:
            await task_data_process.success_handler.handle_success(context)

    @db_transaction
    async def _execute_after_task(
        self, context: Context, task_data_process: TaskDataProcess
    ):
        """
        执行任务后操作
        :param context: 上下文
        :param task_data_process: 任务类型上下文
        :return:
        """
        for after_exec in task_data_process.after_execs:
            await after_exec.execute(context)
        if self.__app.context.after_executor:
            await self.__app.context.after_executor.execute(context)
