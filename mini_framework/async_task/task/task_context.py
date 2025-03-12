from pydantic import Field

from mini_framework.async_task.task.task import Task
from mini_framework.web.std_models.base_model import BaseViewModel


class Context(BaseViewModel):
    """
    上下文
    """

    task: Task = Field(..., description="任务")
    context_id: str = Field(..., description="上下文ID")  # 上下文ID
