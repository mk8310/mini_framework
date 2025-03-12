from starlette.types import ASGIApp

from mini_framework.web.middlewares.base import MiddlewareBase, ResponseManager
from mini_framework.web.request_context import RequestContext


class CacheMiddleware(MiddlewareBase):
    def initialize(self, app: ASGIApp):
        pass

    async def before_request(self, request: RequestContext):
        pass

    async def after_request(self, request: RequestContext, response_manager: ResponseManager):
        pass
