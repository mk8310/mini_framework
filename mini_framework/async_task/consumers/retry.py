import time
from abc import ABC, abstractmethod

from ..task.task import Task
from mini_framework.async_task.task.task_context import Context


class TaskRetry(ABC):
    def __init__(self, consumer, max_attempts: int = 3, delay: int = 1, backoff: int = 2):
        """
        任务重试策略
        :param max_attempts: 最大重试次数
        :param delay: 重试延迟时间
        :param backoff: 重试延迟时间的指数增长
        """
        self.__consumer = consumer
        self.__max_attempts = max_attempts
        self.__delay = delay
        self.__backoff = backoff

    @property
    def max_attempts(self):
        return self.__max_attempts

    @property
    def delay(self):
        return self.__delay

    @property
    def backoff(self):
        return self.__backoff

    @property
    def consumer(self):
        return self.__consumer

    @abstractmethod
    async def retry(self, context: 'Context', error: Exception) -> 'Task':
        raise NotImplementedError('retry method must be implemented')


class NormalTaskRetry(TaskRetry):
    def __init__(self, consumer):
        """
        任务重试策略
        """
        from ..config import task_service_config
        retry_config = task_service_config.retry
        max_attempts = retry_config.max_attempts or 3
        delay = retry_config.delay or 1
        backoff = retry_config.backoff or 2
        super().__init__(consumer, max_attempts, delay, backoff)

    async def retry(self, context: 'Context', error: Exception) -> 'Task':
        """
        重试任务
        :param context: 任务
        :param error: 错误异常信息
        :return:
        """
        task = context.task
        if task.retry_count < self.max_attempts:
            task.retry_count += 1
            task.next_execution_time = time.time() + self.delay * (self.backoff ** task.retry_count)
            return task
        else:
            return None
