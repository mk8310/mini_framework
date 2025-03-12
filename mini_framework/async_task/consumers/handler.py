from abc import ABC, abstractmethod


class TaskSuccessHandler(ABC):
    """
    任务成功处理器
    """

    def __init__(self, task_type, consumer):
        """
        初始化任务成功处理器
        :param task_type: 任务类型
        """
        self.__task_type = task_type
        self.__consumer = consumer

    @property
    def consumer(self):
        return self.__consumer

    @property
    def task_type(self):
        return self.__task_type

    @abstractmethod
    async def handle_success(self, context):
        pass
