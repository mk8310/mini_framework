from fastapi import FastAPI

from ..configurations.errors import ConfigurationError
from ..context import env
from ..design_patterns.singleton import singleton
from ..utils.log import logger
from ..web.middlewares.base import HandlerRegister


@singleton
class ApplicationConfig:

    def __init__(self):
        from mini_framework.configurations import config_injection

        manager = config_injection.get_config_manager()
        app_settings = manager.get_domain_config("web_server")
        if app_settings is None:
            raise ConfigurationError("app_settings is None")
        self.title = app_settings.get("title", "Mini Server")
        self.description = app_settings.get("description", "Mini Server")
        self.version = app_settings.get("version", env.app_version)
        self.name = app_settings.get("name", env.app_name)
        self.need_auth = app_settings.get("need_auth", True)
        self.multi_tenant = app_settings.get("multi_tenant", False)
        self.server_id = app_settings.get("snowflake_service_id", None)
        self.worker_id = app_settings.get("snowflake_worker_id", None)


app_config = ApplicationConfig()


class Application(FastAPI):
    def __init__(self, **kwargs):
        logger.info(f"App name: {app_config.name} initializing.")
        super().__init__(**kwargs)

        self.app_name = app_config.name
        self.app_version = app_config.version
        self.app_root = env.app_root
        HandlerRegister(self).register()
