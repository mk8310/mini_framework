import os

from pydantic import Field

from mini_framework.design_patterns.singleton import singleton
from mini_framework.web.std_models.base_model import BaseViewModel


class SeatunnelConfig(BaseViewModel):
    """
    Seatunnel配置
    """

    app_path: str = Field(..., description="Seatunnel应用路径")
    config_path: str = Field(..., description="Seatunnel配置文件路径")
    maven_domain: str = Field(..., description="Maven仓库域名")
    plugin_paths: list[str] = Field(None, description="Seatunnel插件路径")

    def __post_init__(self):
        self.app_path = self.app_path.strip()
        self.config_path = self.config_path.strip()
        self.maven_domain = self.maven_domain.strip() if self.maven_domain else ""
        self.maven_domain = (
            self.maven_domain
            if self.maven_domain
            else "https://repo1.maven.org/maven2/"
        )

        if not self.maven_domain.endswith("/"):
            self.maven_domain = self.maven_domain + "/"

        if not self.app_path.endswith("/"):
            self.app_path += "/"
        if not self.config_path.endswith("/"):
            self.config_path += "/"

        self.app_path = self.app_path.replace("\\", "/")
        self.config_path = self.config_path.replace("\\", "/")

        if not os.path.exists(self.app_path):
            raise ValueError(f"Seatunnel应用路径不存在: {self.app_path}")

        if not os.path.exists(self.config_path):
            os.makedirs(self.config_path, exist_ok=True)

        if not self.plugin_paths:
            self.plugin_paths = [self.app_path + "lib/", self.app_path + "connectors/"]
        else:
            plugin_paths = [path.strip() for path in self.plugin_paths if path.strip()]
            self.plugin_paths = []
            for path in plugin_paths:
                if not os.path.exists(path):
                    raise ValueError(f"Seatunnel插件路径不存在: {path}")
                if not path.endswith("/"):
                    path += "/"
                path = path.replace("\\", "/")
                if path not in self.plugin_paths:
                    self.plugin_paths.append(path)


@singleton
class DataProcessConfig:
    def __init__(self):
        """
        数据处理配置
        """
        from mini_framework.configurations import config_injection

        manager = config_injection.get_config_manager()
        data_process_config_dict = manager.get_domain_config("data-process")
        if not data_process_config_dict:
            return
        seatunnel_dict = data_process_config_dict.get("seatunnel", {})
        self.seatunnel: SeatunnelConfig = SeatunnelConfig(**seatunnel_dict)


data_process_config = DataProcessConfig()
