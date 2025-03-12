from abc import ABC, abstractmethod
from typing import Any

from mini_framework.data.tasks.datatask import DataTask


class Handler(ABC):
    """
    数据处理任务链的处理器接口
    """
    @abstractmethod
    def set_next(self, handler):
        pass

    @abstractmethod
    def handle(self, data: Any) -> Any:
        pass


class AbstractHandler(Handler):
    """
    数据处理任务链的抽象处理器类
    """
    _next_handler: Handler = None

    def set_next(self, handler: Handler) -> Handler:
        """
        设置下一个处理器
        :param handler: 下一个处理器
        :return: 下一个处理器
        """
        self._next_handler = handler
        return handler

    @abstractmethod
    def handle(self, data: Any) -> Any:
        """
        处理数据
        :param data: 输入数据
        :return: 处理后的数据
        """
        if self._next_handler:
            return self._next_handler.handle(data)
        return None


class TaskHandler(AbstractHandler):
    """
    数据处理任务链的任务处理器
    """
    def __init__(self, task: DataTask):
        self.task = task

    def handle(self, data: Any) -> Any:
        """
        处理数据
        :param data: 输入数据
        :return: 处理后的数据
        """
        self.task.set_data(data)
        data = self.task.execute()
        if self._next_handler:
            return self._next_handler.handle(data)
        return data


class DataProcessor:
    """
    数据处理任务链的处理器
    """
    def __init__(self):
        """
        初始化数据处理任务链的处理器
        """
        self.head: Handler = None
        self.tail: Handler = None

    def add_task(self, task: DataTask):
        task_handler = TaskHandler(task)
        if not self.head:
            self.head = task_handler
            self.tail = task_handler
        else:
            self.tail.set_next(task_handler)
            self.tail = task_handler

    def process(self, initial_data: Any = None):
        if self.head:
            return self.head.handle(initial_data)
        return initial_data
