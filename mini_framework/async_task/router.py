from __future__ import annotations

from typing import Type, List

from .consumers import TaskExecutor, TaskSuccessHandler
from .consumers.task_data_processor import TaskDataProcess
from .task.task_type import TaskType
from ..design_patterns.singleton import singleton
from ..web.std_models.base_model import BaseViewModel


@singleton
class TaskRouterRegistry:
    def __init__(self):
        self.__registries: dict[str, tuple[TaskType, TaskDataProcess]] = dict()

    def register(
        self,
        code,
        consumer_group_id,
        topic,
        name,
        executor_cls: Type[TaskExecutor],
        description,
        max_retry_count=3,
        timeout=3600,
        retry_interval=60,
        retry_backoff=1.0,
        retry_delay=0,
        retry_delay_backoff=1.0,
        retry_delay_max=0,
        retry_delay_max_count=0,
        payload_cls: Type[BaseViewModel] | Type[List[BaseViewModel]] = None,
        payload_is_list: bool = False,
        success_handler_cls: Type[TaskSuccessHandler] = None,
    ):
        """
        注册任务类型
        :param code: 任务类型编码
        :param consumer_group_id: 消费者组ID
        :param topic: 任务订阅的topic
        :param name: 任务名称
        :param executor_cls: 任务执行器类
        :param description: 任务描述
        :param max_retry_count: 最大重试次数
        :param timeout: 任务超时时间
        :param retry_interval: 重试间隔时间
        :param retry_backoff: 重试间隔时间的指数增长系数，用于计算下次重试的时间间隔
        :param retry_delay: 重试延迟时间
        :param retry_delay_backoff: 重试延迟时间的指数增长系数，用于计算下次重试的时间间隔
        :param retry_delay_max: 重试延迟时间最大值
        :param retry_delay_max_count: 重试延迟时间最大值的重试次数
        :param payload_cls: 任务参数模型
        :param payload_is_list: 是否是列表
        :param success_handler_cls: 任务成功处理器类
        :return: None
        """
        task_type = TaskType(
            code=code,
            name=name,
            description=description,
            max_retry_count=max_retry_count,
            timeout=timeout,
            retry_interval=retry_interval,
            retry_backoff=retry_backoff,
            retry_delay=retry_delay,
            retry_delay_backoff=retry_delay_backoff,
            retry_delay_max=retry_delay_max,
            retry_delay_max_count=retry_delay_max_count,
            payload_cls=payload_cls,
            payload_is_list=payload_is_list,
            executor_cls=executor_cls,
            success_handler_cls=success_handler_cls,
            consumer_group_id=consumer_group_id,
            topic=topic,
        )
        if code in self.__registries:
            raise ValueError(f"Task type {code} already exists.")
        task_type_manager = TaskDataProcess(task_type)
        self.__registries[code] = (task_type, task_type_manager)

    def get_task_type(self, code: str) -> TaskType | None:
        """
        获取任务类型
        :param code: 任务类型编码
        :return: 任务类型
        """
        task_type = self.__registries.get(code)
        if task_type:
            return task_type[0]
        return None

    def get_task_data_processor(self, code: str) -> TaskDataProcess | None:
        """
        获取任务数据处理器
        :param code: 任务类型编码
        :return: 任务数据处理器
        """
        task_type = self.__registries.get(code)
        if task_type:
            return task_type[1]
        return None

    @property
    def task_types(self):
        """
        获取所有任务类型
        :return: 任务类型列表
        """
        return [task_type for task_type, _ in self.__registries.values()]

    @property
    def task_type_topics(self):
        """
        获取所有任务类型名称
        :return: 任务类型名称列表
        """
        return [task_type.topic for task_type in self.task_types]


task_router = TaskRouterRegistry()
