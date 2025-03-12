from .executor import TaskExecutor


class DatabaseReleaseExecutor(TaskExecutor):

    async def execute(self, context):
        from ...databases.conn_managers.db_manager import db_connection_manager

        await db_connection_manager.clear_async_session()
