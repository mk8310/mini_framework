from __future__ import annotations

from typing import Type

from pydantic import Field

from ..consumers.executor import TaskExecutor
from ..consumers.handler import TaskSuccessHandler
from ...web.std_models.base_model import BaseViewModel


class TaskType(BaseViewModel):
    topic: str = Field(..., description="Kafka主题")
    consumer_group_id: str = Field(..., description="消费者组ID")
    code: str = Field(..., description="任务类型编码")
    name: str = Field(..., description="任务名称")
    description: str = Field(..., description="任务描述")
    max_retry_count: int = Field(3, description="最大重试次数")
    timeout: int = Field(3600, description="超时时间")
    retry_interval: int = Field(60, description="重试间隔时间")
    retry_backoff: float = Field(1.0, description="重试间隔时间的指数增长系数")
    retry_delay: int = Field(0, description="重试延迟时间")
    retry_delay_backoff: float = Field(1.0, description="重试延迟时间的指数增长系数")
    retry_delay_max: int = Field(0, description="重试延迟时间最大值")
    retry_delay_max_count: int = Field(0, description="重试延迟时间最大值的重试次数")
    payload_cls: Type[BaseViewModel] | dict | None = Field(None, description="任务参数模型")
    payload_is_list: bool = Field(False, description="是否是列表")
    executor_cls: Type[TaskExecutor] = Field(None, description="任务执行器")
    success_handler_cls: Type[TaskSuccessHandler] | None = Field(
        None, description="任务成功处理器"
    )
