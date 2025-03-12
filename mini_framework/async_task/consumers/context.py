from mini_framework.utils.log import logger


class TaskTypeContext:
    def __init__(self):
        from mini_framework.async_task.task.task_type import TaskType

        self.__task_type: TaskType = None
        self.__executor_inst = None
        self.__before_execute_instances: list = []
        self.__after_execute_instances: list = []
        self.__success_handler = None
        self.__initialize = False

    @property
    def task_type(self):
        """
        任务类型
        :return:
        """
        return self.__task_type

    @property
    def executor(self):
        """
        任务执行类实例
        :return:
        """
        return self.__executor_inst

    @property
    def before_execs(self):
        """
        :return:
        """
        return self.__before_execute_instances

    @property
    def after_execs(self):
        return self.__after_execute_instances

    @property
    def success_handler(self):
        return self.__success_handler

    def initialize(self, task_type):
        self.__task_type = task_type

    def prepare(self, consumer):
        """
        准备任务执行器
        :param consumer: 消费者
        :return:
        """
        if self.__initialize:
            return

        from mini_framework.async_task.consumers import TaskExecutor
        from mini_framework.async_task.consumers import TaskSuccessHandler

        if self.__task_type.executor_cls and issubclass(
            self.__task_type.executor_cls, TaskExecutor
        ):
            self.__executor_inst = self.__task_type.executor_cls()
            self.__executor_inst.prepare(self.__task_type, consumer)
        else:
            raise ValueError(f"Task type {self.__task_type.code} has no executor.")

        if self.__task_type.success_handler_cls and issubclass(
            self.__task_type.success_handler_cls, TaskSuccessHandler
        ):
            self.__success_handler = self.__task_type.success_handler_cls(
                self.__task_type, consumer
            )
        else:
            logger.warning(f"Task type {self.__task_type.code} has no success handler.")

        if not self.__task_type.payload_cls:
            raise ValueError("Payload class is required")

        self.__initialize = True
