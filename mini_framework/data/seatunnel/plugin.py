from abc import ABC, abstractmethod

from mini_framework.data.seatunnel.config import Config


class Plugin(Config, ABC):
    """Seatunnel 插件配置类"""

    def __init__(self, plugin, **kwargs):
        self.plugin = plugin
        self.config = kwargs

    def validate(self):
        if self.plugin is None or self.plugin == "":
            raise ValueError("plugin 不能为空")

    def _to_dict(self) -> dict:
        return {self.plugin: self.to_plugin_dict()}

    @abstractmethod
    def to_plugin_dict(self) -> dict:
        pass
