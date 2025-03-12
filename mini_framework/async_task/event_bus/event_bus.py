import asyncio
from datetime import datetime
from threading import Lock
from typing import Callable

import shortuuid

from .event import Event, TaskEvent
from ..consumers.event_type import EventType
from mini_framework.async_task.task.task_context import Context
from ...databases.entities.db_executor import db_transaction


def get_event(
    context: Context,
    event_type: EventType = None,
    ex: Exception = None,
    *args,
    **kwargs
) -> Event:
    """
    Get event from event type
    :param context: 上下文
    :param ex: 异常信息
    :param event_type:
    :param args:
    :param kwargs:
    :return:
    """
    timestamp = datetime.now()
    return TaskEvent(context, timestamp, event_type, *args, **kwargs)


@db_transaction
async def event_handler(handle, event: "Event"):
    """
    处理任务状态变更事件
    :param handle: 任务事件处理器
    :param event: 任务事件
    :return:
    """
    await handle(event)


class EventBus:
    _instance = None
    _lock = Lock()

    def __init__(self):
        self.handlers = {}

    def __new__(cls):
        with cls._lock:  # 确保实例化的线程安全
            if cls._instance is None:
                cls._instance = super(EventBus, cls).__new__(cls)
                cls._instance.handlers = {}
        return cls._instance

    def subscribe(self, event_type: EventType, handler: Callable):
        with self._lock:
            if event_type not in self.handlers:
                self.handlers[event_type] = []
            self.handlers[event_type].append(handler)

    def unsubscribe(self, event_type: EventType, handler: Callable):
        with self._lock:
            if event_type in self.handlers and handler in self.handlers[event_type]:
                self.handlers[event_type].remove(handler)

    async def publish(self, event: "Event"):
        handlers_to_call = []
        with self._lock:  # 复制一份处理器列表，以避免在异步调用中持有锁
            if event.event_type in self.handlers:
                handlers_to_call = list(self.handlers[event.event_type])

        if handlers_to_call:
            await asyncio.gather(
                *(event_handler(handler, event) for handler in handlers_to_call)
            )


event_bus = EventBus()
