from datetime import datetime
from enum import Enum
from typing import Union, List

from pydantic import Field

from mini_framework.web.std_models.base_model import BaseViewModel


class TaskState(str, Enum):
    """
    任务状态
    """

    pending = "pending"  # 待处理
    running = "running"  # 运行中
    completed = "completed"  # 完成
    succeeded = "succeeded"  # 成功
    failed = "failed"  # 失败
    aborted = "aborted"  # 中止
    cancelled = "cancelled"  # 取消
    timeout = "timeout"  # 超时


class Task(BaseViewModel):
    """
    任务
    """

    task_type: str = Field(..., description="任务类型")
    payload: Union[BaseViewModel, list[BaseViewModel], None] = Field(
        None, description="任务参数"
    )
    state: TaskState = Field(
        TaskState.pending, description="任务状态"
    )  # TaskState.pending  # 任务状态
    task_id: str = Field(None, description="任务ID")  # 任务ID
    app_id: str = Field(None, description="应用ID")  # 应用ID
    operator: str = Field(None, description="操作人")  # 操作人
    created_at: datetime = Field(None, description="创建时间")  # 创建时间
    progress: float = Field(0, description="任务进度")  # 任务进度
    process_desc: str = Field("", description="任务进度描述")  # 任务进度描述
    source_file: str = Field("", description="源文件")  # 源文件
    result_bucket: str = Field("", description="结果桶")  # 结果桶
    result_file: str = Field("", description="结果文件")  # 结果文件
    completed_time: datetime = Field(None, description="完成时间")  # 完成时间
    result_extra: dict = Field(dict(), description="额外结果")  # 额外结果
    retry_count: int = Field(0, description="重试次数")  # 重试次数
    next_execution_time: float = Field(None, description="下次执行时间")  # 下次执行时间


class BatchTasks(BaseViewModel):
    """
    批次任务
    """

    tasks: List["Task"]  # 任务列表
