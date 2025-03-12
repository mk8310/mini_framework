from abc import ABC, abstractmethod

from ..event_bus import event_bus
from ..task.task_context import Context


class TaskExecutor(ABC):
    """
    任务执行器
    """

    def __init__(self):
        """
        初始化任务执行器
        """
        from ..consumers import TaskConsumer

        self.__consumer: "TaskConsumer" = None
        self.__task_type = None
        self.__event_bus = event_bus

    def prepare(self, task_type, consumer):
        """
        准备执行器
        :return:
        """
        self.__task_type = task_type
        self.__consumer = consumer

    @property
    def consumer(self):
        return self.__consumer

    @property
    def event_bus(self):
        return self.__event_bus

    @abstractmethod
    async def execute(self, context: "Context"):
        pass


class BeforeExecutor(TaskExecutor, ABC):
    pass


class AfterExecutor(TaskExecutor, ABC):
    pass
