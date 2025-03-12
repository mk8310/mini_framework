from contextlib import asynccontextmanager

import uvicorn

from mini_framework.design_patterns.singleton import singleton
from mini_framework.utils.http import HTTPRequest
from mini_framework.web.api_doc_manager import APIDocumentManager
from mini_framework.web.middlewares.auth import AuthMiddleware
from mini_framework.web.middlewares.base import (
    RequestProcessMiddleware,
    middleware_manager,
)
from mini_framework.web.middlewares.cache import CacheMiddleware
from mini_framework.web.middlewares.database import DatabaseMiddleware
from mini_framework.web.middlewares.limit import LimitMiddleware
from mini_framework.web.middlewares.log import LogMiddleware
from mini_framework.web.mini_app import Application, app_config
from mini_framework.web.router import root_router


@asynccontextmanager
async def lifespan(app: Application):
    http_req = HTTPRequest()
    http_req.startup()
    yield
    await http_req.shutdown()
    from mini_framework.message_queue.kafka_utils import kafka_producer
    await kafka_producer.stop()


@singleton
class ApplicationContextManager(object):
    def __init__(self):
        self.__app: Application = None
        self.app_config = dict(
            title=f"{app_config.name} Server",
            description=f"{app_config.name} Server",
            version=app_config.version,
            openapi_url=f"/api/{app_config.name}/openapi.json",
            lifespan=lifespan,
        )

    def initialize(self):
        middleware_manager.register(LogMiddleware)
        middleware_manager.register(DatabaseMiddleware)
        middleware_manager.register(LimitMiddleware)
        middleware_manager.register(AuthMiddleware)
        middleware_manager.register(CacheMiddleware)
        manager = APIDocumentManager()
        # self.app_config.update(manager.config)
        self.__app = Application(**self.app_config)
        self.__app.add_middleware(RequestProcessMiddleware)
        router = root_router.get_router()
        self.__app.include_router(router)
        manager.register(self.__app)

    def run(self, host="127.0.0.1", port=8088):
        uvicorn.run(self.app, host=host, port=port)

    @property
    def app(self) -> Application:
        return self.__app


application_context_manager = ApplicationContextManager()
