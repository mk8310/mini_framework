from datetime import datetime

from sqlalchemy import JSON, BigInteger
from sqlalchemy.orm import Mapped, mapped_column

from mini_framework.databases.entities import BaseDBModel


class TaskInfo(BaseDBModel):
    """
    任务表模型
    """

    __tablename__ = "mini_tasks"
    __table_args__ = {"comment": "任务表模型"}

    task_id: Mapped[str] = mapped_column(primary_key=True, comment="任务ID")
    task_type: Mapped[str] = mapped_column(comment="任务类型")
    payload: Mapped[dict] = mapped_column(JSON, comment="任务负载")
    app_id: Mapped[str] = mapped_column(comment="应用ID")
    operator: Mapped[str] = mapped_column(comment="操作人")
    created_at: Mapped[datetime] = mapped_column(comment="创建时间")
    source_file: Mapped[str] = mapped_column(comment="源文件")


class TaskProgress(BaseDBModel):
    """
    任务进度表模型
    """

    __tablename__ = "mini_task_progress"
    __table_args__ = {"comment": "任务进度表模型"}

    progress_id: Mapped[str] = mapped_column(
        primary_key=True, comment="进度ID"
    )
    task_id: Mapped[str] = mapped_column(index=True, comment="任务ID")
    progress: Mapped[float] = mapped_column(comment="任务进度")
    progress_desc: Mapped[str] = mapped_column(
        comment="任务进度描述", nullable=True, default=""
    )
    last_updated: Mapped[datetime] = mapped_column(comment="最后更新时间")


class TaskResult(BaseDBModel):
    """
    任务结果表模型
    """

    __tablename__ = "mini_task_results"
    __table_args__ = {"comment": "任务结果表模型"}

    result_id: Mapped[str] = mapped_column(primary_key=True, comment="结果ID")
    task_id: Mapped[str] = mapped_column(index=True, comment="任务ID")
    result_extra: Mapped[dict] = mapped_column(JSON, comment="任务额外结果")
    state: Mapped[str] = mapped_column(comment="任务状态")
    last_updated: Mapped[datetime] = mapped_column(comment="完成时间")
    result_file: Mapped[str] = mapped_column(comment="结果文件")
    result_bucket: Mapped[str] = mapped_column(comment="结果桶", nullable=True)
    result_file_id: Mapped[int] = mapped_column(
        BigInteger, comment="结果文件ID", nullable=True
    )
