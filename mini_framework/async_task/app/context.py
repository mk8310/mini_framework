import shortuuid

from mini_framework.async_task.consumers.executor import (
    AfterExecutor,
    BeforeExecutor,
)
from mini_framework.async_task.errors import InvalidExecutorTypeError
from mini_framework.design_patterns.singleton import singleton

frozen_keys = [
    "app_root",
    "app_name",
    "app_version",
    "app_env",
    "app_debug",
    "app_config",
    "app_context",
    "app_logger",
]


def _check_executor_instance(executor, expected_type):
    if not isinstance(executor, expected_type):
        raise InvalidExecutorTypeError(executor, expected_type)


@singleton
class ApplicationContext(object):
    def __init__(self):
        self.__before_executor = None
        self.__after_executor = None
        self._context = {}

    def set(self, key, value):
        self._context[key] = value

    def get(self, key):
        return self._context.get(key, None)

    def __str__(self):
        return str(self._context)

    def __repr__(self):
        return str(self)

    def __iter__(self):
        return iter(self._context.items())

    def __len__(self):
        return len(self._context)

    def __contains__(self, key):
        return key in self._context

    def __getitem__(self, key):
        return self.get(key)

    def __setitem__(self, key, value):
        self.set(key, value)

    def __delitem__(self, key):
        del self._context[key]

    def clear(self):
        raise NotImplementedError("This method is not implemented.")

    def keys(self):
        return self._context.keys()

    def values(self):
        return self._context.values()

    def items(self):
        return self._context.items()

    def update(self, other):
        self._context.update(other)

    def copy(self):
        return self._context.copy()

    def pop(self, key, default=None):
        return self._context.pop(key, default)

    def popitem(self):
        return self._context.popitem()

    def __eq__(self, other):
        return self._context == other

    def __ne__(self, other):
        return self._context != other

    @property
    def before_executor(self):
        return self.__before_executor

    @before_executor.setter
    def before_executor(self, executor):
        _check_executor_instance(executor, BeforeExecutor)
        self.__before_executor = executor

    @property
    def after_executor(self):
        return self.__after_executor

    @after_executor.setter
    def after_executor(self, executor):
        _check_executor_instance(executor, AfterExecutor)
        self.__after_executor = executor

    @property
    def app(self):
        if "app" not in self._context:
            return None
        task_app = self.get("app")
        if not task_app:
            raise ValueError("App is not found in the context.")
        from .app import TaskApplication

        if not isinstance(task_app, TaskApplication):
            raise ValueError("App must be an instance of TaskApplication.")
        return task_app

    @property
    def app_id(self):
        """
        获取应用程序 ID
        :return:
        """
        if "app_id" not in self._context:
            self._context["app_id"] = shortuuid.uuid()
        return self._context["app_id"]
