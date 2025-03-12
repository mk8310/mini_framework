import os
import threading

from mini_framework.design_patterns.singleton import singleton


@singleton
class SystemEnvironment(object):
    """
    系统环境变量管理器
    """

    __instance = None
    __env = None

    def __new__(cls, *args, **kwargs):
        lock = threading.Lock()
        lock.acquire()
        try:
            if not cls.__instance:
                cls.__instance = object.__new__(cls)
        finally:
            lock.release()
        return cls.__instance

    def __init__(self):
        if not self.__env:
            self.__env = os.environ

    def __getitem__(self, key):
        return self.__env[key]

    def __setitem__(self, key, value):
        if not isinstance(value, str):
            value = str(value)
        self.__env[key] = value

    def __delitem__(self, key):
        if key in self.__env:
            del self.__env[key]

    def __contains__(self, key):
        return key in self.__env

    def __iter__(self):
        return iter(self.__env)

    def __len__(self):
        return len(self.__env)

    def items(self):
        return self.__env.items()

    def get(self, key, default=None):
        if key in self.__env:
            return self.__env[key]
        return default

    def set(self, key, value):
        self.__env[key] = value

    def unset(self, key):
        if key in self.__env:
            del self.__env[key]

    def get_all(self):
        return self.__env

    def set_all(self, env):
        self.__env = env

    def unset_all(self):
        self.__env = {}

    @property
    def app_root(self):
        return self.get("APP_ROOT")

    @app_root.setter
    def app_root(self, svc_root):
        self.set("APP_ROOT", svc_root)

    def unset_app_root(self):
        self.unset("APP_ROOT")

    @property
    def sync_type(self):
        return self.get("SYNC_TYPE", "async")

    @sync_type.setter
    def sync_type(self, sync_type):
        self.set("SYNC_TYPE", sync_type)

    def unset_sync_type(self):
        self.unset("SYNC_TYPE")

    @property
    def app_name(self):
        return self.get("APP_NAME")

    def set_app_name(self, svc_name):
        self.set("APP_NAME", svc_name)

    def unset_app_name(self):
        self.unset("APP_NAME")

    @property
    def app_version(self):
        return self.get("APP_VERSION")

    def set_app_version(self, svc_version):
        self.set("APP_VERSION", svc_version)

    def unset_app_version(self):
        self.unset("APP_VERSION")

    @property
    def config_path(self):
        return self.get("CONFIG_PATH")

    def set_config_path(self, config_path):
        self.set("CONFIG_PATH", config_path)

    def unset_config_path(self):
        self.unset("CONFIG_PATH")

    @property
    def config_reader(self):
        return self.get("CONFIG_READER")

    def set_config_reader(self, config_reader):
        self.set("CONFIG_READER", config_reader)

    def unset_config_reader(self):
        self.unset("CONFIG_READER")

    @property
    def config_reader_cls(self) -> str:
        return self.get("CONFIG_READER_CLS", "json-config-reader")

    def set_config_reader_cls(self, config_reader_cls):
        self.set("CONFIG_READER_CLS", config_reader_cls)

    def unset_config_reader_cls(self):
        self.unset("CONFIG_READER_CLS")

    @property
    def debug(self):
        result = self.get("DEBUG", False)
        if isinstance(result, bool):
            return result
        if result.lower() == "true":
            return True
        return False

    @debug.setter
    def debug(self, debug):
        self.set("DEBUG", debug)

    @property
    def app_config(self):
        return self.get("APP_CONFIG")
