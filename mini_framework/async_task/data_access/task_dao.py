from sqlalchemy import select, update, delete

from mini_framework.async_task.data_access.models import (
    TaskInfo,
    TaskProgress,
    TaskResult,
)
from mini_framework.databases.entities.dao_base import DAOBase


class TaskDAO(DAOBase):
    """
    异步任务数据访问对象
    """

    async def add_task(self, task: TaskInfo, is_commit=False):
        """
        添加任务
        :param task: 任务
        :param is_commit: 是否提交
        :return:
        """
        session = await self.master_db()
        session.add(task)
        return task

    async def add_task_progress(self, task_progress: TaskProgress, is_commit=False):
        """
        添加任务进度
        :param task_progress: 任务
        :param is_commit: 是否提交
        :return:
        """
        session = await self.master_db()
        session.add(task_progress)
        return task_progress

    async def add_task_result(self, task_results: TaskResult, is_commit=False):
        """
        添加任务结果
        :param is_commit: 是否提交
        :param task_results: 任务结果
        :return:
        """
        session = await self.master_db()
        session.add(task_results)
        return task_results

    async def get_task_result_by_id(self, task_id: str) -> TaskResult:
        """
        通过任务ID获取任务结果
        :param task_id: 任务ID
        :return:
        """
        session = await self.slave_db()
        result = await session.execute(
            select(TaskResult)
            .filter(TaskResult.task_id == task_id)
            .order_by(TaskResult.last_updated.desc())
            .limit(1)
        )
        return result.scalar()

    async def get_task_by_id(self, task_id: str) -> TaskInfo:
        """
        通过任务ID获取任务
        :param task_id: 任务ID
        :return:
        """
        session = await self.slave_db()
        result = await session.execute(
            select(TaskInfo).filter(TaskInfo.task_id == task_id)
        )
        return result.scalar()

    async def update_task(self, task_id, update_detail):
        """
        更新任务信息
        :param task_id: 任务ID
        :param update_detail: 更新内容
        :return:
        """
        if len(update_detail) == 0:
            return
        session = await self.master_db()
        query = (
            update(TaskInfo).filter(TaskInfo.task_id == task_id).values(update_detail)
        )
        await session.execute(query)

    async def delete_task(self, task_id):
        session = await self.master_db()
        query = delete(TaskInfo).where(TaskInfo.task_id == task_id)
        await session.execute(query)
