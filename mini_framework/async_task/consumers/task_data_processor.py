from ..task.task_type import TaskType
from ..task.task import Task
from ...utils.log import logger


class TaskDataProcess:
    """
    任务数据处理器
    """

    def __init__(self, task_type: TaskType):
        """
        初始化任务数据处理器
        :param task_type:
        """
        self.__task_type = task_type
        self.__executor_inst = None
        self.__before_execute_instances: list = []
        self.__after_execute_instances: list = []
        self.__success_handler = None
        self.__initialize = False

    def verify_payload(self, task: Task):
        """
        验证任务参数,需要根据任务类型进行验证:
        1. 若任务类型没有定义payload类型，则不验证;
        2. 若任务类型的payload_is_list为True，则验证参数是否为list并且list中的元素是否为payload_cls类型;
        3. 否则验证参数是否为payload_cls类型
        :param task:
        :return:
        """
        if self.__task_type.payload_cls is None:
            return
        if self.__task_type.payload_is_list and not isinstance(task.payload, list):
            raise ValueError(
                f"Invalid payload class, must be {self.__task_type.payload_cls}"
            )
        payload_list = []
        if not self.__task_type.payload_is_list:
            payload_list.append(task.payload)
        else:
            payload_list = task.payload
        type_error_list = []
        index = 0
        for payload in payload_list:
            if not isinstance(payload, self.__task_type.payload_cls):
                type_error_list.append(index)
            index += 1
        if len(type_error_list) > 0 and self.__task_type.payload_is_list:
            raise ValueError(
                f"Invalid payload class, must be {self.__task_type.payload_cls}, error index: {type_error_list}"
            )
        elif len(type_error_list) > 0 and not self.__task_type.payload_is_list:
            raise ValueError(
                f"Invalid payload class, must be {self.__task_type.payload_cls}"
            )

    def serialize_task(self, task: Task):
        """
        序列化任务
        :param task: 任务
        :return:
        """
        self.verify_payload(task)
        payload_dict = {}
        if self.__task_type.payload_cls == "none":
            pass
        elif self.__task_type.payload_is_list and isinstance(task.payload, list):
            payload_dict = [
                payload.model_dump() for payload in task.payload
            ]  # .model_dump()
        else:
            payload_dict = task.payload.model_dump()
        result = task.model_dump()
        result["payload"] = payload_dict
        return result

    def deserialize_task(self, task_dict: dict):
        """
        反序列化任务
        :param task_dict: 任务字典
        :return:
        """
        task_dict = {k: v for k, v in task_dict.items() if v is not None}
        payload = task_dict.pop("payload")
        if self.__task_type.payload_cls == list:
            task_dict["payload"] = [
                self.__task_type.payload_cls(**item) for item in payload
            ]
        elif self.__task_type.payload_cls is not None:
            task_dict["payload"] = self.__task_type.payload_cls(**payload)
        else:
            task_dict["payload"] = payload
        return Task(**task_dict)

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
