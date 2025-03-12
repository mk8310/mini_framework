from datetime import datetime

import shortuuid

from ..data_access.models import TaskInfo, TaskProgress, TaskResult
from ..data_access.task_dao import TaskDAO
from ..task.task import Task, TaskState
from ...databases.entities import to_dict
from ...design_patterns.depend_inject import dataclass_inject
from ...web.toolkit.model_utilities import view_model_to_orm_model


@dataclass_inject
class TaskRule(object):
    task_dao: TaskDAO

    async def create_task(self, task: Task):
        """
        添加新任务
        :param task: 任务
        :return:
        """
        task_info: TaskInfo = view_model_to_orm_model(task, TaskInfo)
        task_info.last_updated = datetime.now()
        task_progress: TaskProgress = view_model_to_orm_model(task, TaskProgress)
        task_progress.progress_id = shortuuid.uuid()
        task_progress.last_updated = datetime.now()
        task_progress.progress_desc = ""
        task_progress.task_id = task.task_id
        task_results: TaskResult = view_model_to_orm_model(task, TaskResult)
        task_results.result_id = shortuuid.uuid()
        task_results.last_updated = datetime.now()
        task_results.state = task.state
        task_results.result_extra = task.result_extra
        task_results.result_file = task.result_file
        task_info = await self.task_dao.add_task(task_info)
        task_process = await self.task_dao.add_task_progress(task_progress)
        task_results = await self.task_dao.add_task_result(task_results)
        return task_info, task_process, task_results

    async def upgrade_task(self, task: Task):
        """
        添加任务
        :param task: 任务
        :return:
        """
        old_task = await self.task_dao.get_task_by_id(task.task_id)
        if old_task is None:
            raise Exception(f"Task {task.task_id} not found")

        task_info: TaskInfo = view_model_to_orm_model(task, TaskInfo)
        task_info.last_updated = datetime.now()
        task_progress: TaskProgress = view_model_to_orm_model(task, TaskProgress)
        task_progress.progress_id = shortuuid.uuid()
        task_progress.last_updated = datetime.now()
        task_progress.progress_desc = ""
        task_progress.task_id = task.task_id
        task_results: TaskResult = view_model_to_orm_model(task, TaskResult)
        task_results.result_id = shortuuid.uuid()
        task_results.last_updated = datetime.now()

        update_detail = dict()
        old_task_dict = to_dict(old_task)
        # 比较task_info与old_task的差异，将差异更新到update_detail
        for key, value in task.model_dump().items():
            if key not in old_task_dict.keys():
                continue
            if old_task_dict[key] != value:
                update_detail[key] = value
        task_info = await self.task_dao.update_task(task_info.task_id, update_detail)
        task_process = await self.task_dao.add_task_progress(task_progress)
        task_results = await self.task_dao.add_task_result(task_results)
        return task_info, task_process, task_results

    async def progress_change(
        self,
        task: Task,
        progress: float,
        desc: str,
        state: TaskState,
        result_extra=None,
        result_file: str = "",
    ):
        """
        添加任务进度
        :param task: 任务
        :param progress: 进度
        :param desc: 描述
        :param state: 状态
        :param result_extra: 额外结果
        :param result_file: 结果文件
        :return:
        """
        if result_extra is None:
            result_extra = {}
        task_progress = TaskProgress()
        task_progress.progress_id = shortuuid.uuid()
        task_progress.task_id = task.task_id
        task_progress.last_updated = datetime.now()
        task_progress.progress_desc = desc
        task_progress.progress = progress
        task.progress = progress

        old_task = await self.task_dao.get_task_result_by_id(task.task_id)

        if not old_task or state != old_task.state:
            task.state = state
            task_results = TaskResult()
            task_results.result_id = shortuuid.uuid()
            task_results.task_id = task.task_id
            task_results.state = state
            task_results.result_extra = result_extra
            task_results.result_file = result_file
            task_results.last_updated = datetime.now()
            await self.task_dao.add_task_result(task_results)

        return await self.task_dao.add_task_progress(task_progress)

    def cancel_task(self, task):
        pass
