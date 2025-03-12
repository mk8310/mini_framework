from ..event_bus import TaskEvent
from ..consumers.event_type import EventType
from ..data_access.task_rule import TaskRule
from ..event_bus import event_bus
from ..task.task import TaskState
from ...design_patterns.depend_inject import get_injector
from ...design_patterns.singleton import singleton


@singleton
class TaskEvents:
    async def handle_task_state_change(self, event: 'TaskEvent'):
        """
        处理任务状态变更事件
        :param event: 任务事件
        :return:
        """
        task_rule: TaskRule = get_injector(TaskRule)
        await task_rule.upgrade_task(event.task)

    async def handle_task_progress(self, event: 'TaskEvent'):
        """
        处理任务进度事件
        :param event:
        :return:
        """
        task_rule: TaskRule = get_injector(TaskRule)
        task = event.task
        await task_rule.progress_change(task, task.progress, task.process_desc, task.state)

    async def handle_task_failure(self, event: 'TaskEvent'):
        """
        处理任务失败事件
        :param event:
        :return:
        """
        task_rule: TaskRule = get_injector(TaskRule)
        task = event.task
        task.state = TaskState.failed
        await task_rule.progress_change(task, task.progress, task.process_desc, task.state,
                                        result_extra=task.result_extra, result_file=task.result_file)

    async def handle_task_success(self, event: 'TaskEvent'):
        """
        处理任务成功事件
        :param event:
        :return:
        """
        task_rule: TaskRule = get_injector(TaskRule)
        task = event.task
        task.state = TaskState.succeeded
        await task_rule.progress_change(task, task.progress, task.process_desc, task.state,
                                        result_extra=task.result_extra, result_file=task.result_file)

    async def handle_task_cancel(self, event: 'TaskEvent'):
        """
        处理任务取消事件
        :param event:
        :return:
        """
        task_rule: TaskRule = get_injector(TaskRule)
        await task_rule.cancel_task(event.task)

    def __init__(self):
        event_bus.subscribe(EventType.event, self.handle_task_state_change)
        event_bus.subscribe(EventType.progress, self.handle_task_progress)
        event_bus.subscribe(EventType.failure, self.handle_task_failure)
        event_bus.subscribe(EventType.success, self.handle_task_success)
        event_bus.subscribe(EventType.cancel, self.handle_task_cancel)
