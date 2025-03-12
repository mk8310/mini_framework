from abc import ABC
from datetime import datetime

from ..consumers.event_type import EventType
from mini_framework.async_task.task.task_context import Context


class Event(ABC):
    def __init__(
        self,
        context: "Context",
        timestamp: datetime,
        event_type: EventType,
        *args,
        **kwargs
    ):
        self.timestamp = timestamp
        self.event_type = event_type
        self.args = args
        self.kwargs = kwargs
        self.context = context


class TaskEvent(Event):
    def __init__(
        self,
        context: "Context",
        timestamp: datetime,
        event_type: EventType,
        *args,
        **kwargs
    ):
        super().__init__(context, timestamp, event_type, *args, **kwargs)
        self.context = context
        self.task = context.task
