import threading


class TaskAppFactory:
    _instance = None
    _lock = threading.Lock()

    @classmethod
    def get_instance(cls, *args, **kwargs):
        from .app import TaskApplication

        with cls._lock:
            if cls._instance is None:
                cls._instance = TaskApplication(*args, **kwargs)
            return cls._instance


app = TaskAppFactory.get_instance()
