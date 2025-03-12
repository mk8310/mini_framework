import json
import os
import os.path

from injector import Module, provider, Injector, singleton as inject_singleton
from injector import singleton

from mini_framework.configurations import BaseConfig
from mini_framework.context import env


@singleton
class ConfigManager:
    __content = None

    @classmethod
    def set_cls_content(cls, content: dict):
        cls.__content = content

    def __init__(self):
        self.configs = None
        if self.__content:
            self.configs = ConfigManager.__content
        else:
            self.__read_config()

    def __read_config(self):
        config_path = self.__config_path
        root_config_path = os.path.join(env.app_root, "config.json")
        if not os.path.exists(config_path):
            raise FileNotFoundError(
                "config file not found, "
                "the config path find sequence is: \n"
                "\t1. environment variable 'CONFIG_PATH' \n"
                "\t2. /etc/mini/config.json \n"
                "\t3. {root_config_path}".format(root_config_path=root_config_path)
            )
        with open(config_path, "r", encoding="utf-8") as f:
            self.configs = json.load(f)

    @property
    def __config_path(self):
        """
        获得配置文件路径
        默认使用/etc/mini/config.json，如果不存在则使用当前目录下的config.json，如果都不存在则抛出异常
        :return:
        """

        config_path = env.config_path or ""
        if os.path.exists(config_path):
            return config_path
        if os.path.exists("/etc/mini/config.json"):
            return "/etc/mini/config.json"
        config_path = os.path.join(env.app_root, "config.json")
        if os.path.exists(config_path):
            return config_path
        raise FileNotFoundError(
            "config file not found, "
            "the config path find sequence is: \n"
            "\t1. environment variable 'CONFIG_PATH' \n"
            "\t2. /etc/mini/config.json \n"
            "\t3. {root_config_path}".format(root_config_path=config_path)
        )

    def register_domain_config(self, key, domain_class):
        if key in self.configs:
            self.configs[key] = domain_class(self.configs[key])

    def get_domain_config(self, key) -> dict:
        config = self.configs.get(key, None)
        return config.copy() if config else None

    def __getitem__(self, item):
        return self.configs[item]

    def get(self, item, default=None):
        return self.configs.get(item, default)


class ConfigModule(Module):

    @inject_singleton
    @provider
    def provide_config_manager(self) -> ConfigManager:
        return ConfigManager()


@singleton
class ConfigInjection:
    def __init__(self):
        self.__injector = Injector([ConfigModule()])

    def get_config_manager(self):
        return self.__injector.get(ConfigManager)

    @property
    def injector(self):
        return self.__injector

    def get(self, config_class):
        if not issubclass(config_class, BaseConfig):
            raise ValueError("config_class must be subclass of BaseConfig")
        cls = self.__injector.get(config_class)
        cls.initialize()
        return cls
