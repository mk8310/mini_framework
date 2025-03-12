from starlette.types import ASGIApp

from mini_framework.web.middlewares.base import MiddlewareBase, ResponseManager
from mini_framework.web.request_context import RequestContext


class DatabaseMiddleware(MiddlewareBase):
    def initialize(self, app: ASGIApp):
        pass

    async def before_request(self, request: RequestContext):
        from mini_framework.databases.conn_managers.utilities import database_transaction_id

        database_transaction_id.set(request.request_id)

    async def after_request(
        self, request: RequestContext, response_manager: ResponseManager
    ):
        from mini_framework.databases.conn_managers.db_manager import (
            db_connection_manager,
        )

        await db_connection_manager.clear_async_session()
