import asyncio

from ..commands.command_base import Command
from ..utils.modules import import_callable
import atexit


@atexit.register
def cleanup():
    loop = asyncio.get_event_loop()
    from mini_framework.databases.conn_managers.db_manager import db_connection_manager

    loop.run_until_complete(db_connection_manager.clear_async_session())
    loop.close()


class AsyncTaskCommand(Command):
    def __init__(self, router_func_module: str, **kwargs):
        self.__router_func_module = router_func_module
        super().__init__()

    def run(self, *args, **kwargs):
        from mini_framework.async_task.app.app_factory import app
        from mini_framework.context import env

        env.sync_type = "async"
        router_func = import_callable(self.__router_func_module)
        router_func()
        import asyncio

        loop = asyncio.get_event_loop()
        app_future = app.run()
        loop.run_until_complete(app_future)
        loop.run_forever()
