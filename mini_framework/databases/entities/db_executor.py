import shortuuid


def db_transaction(func):
    async def inner(*args, **kwargs):
        try:
            from mini_framework.databases.conn_managers.utilities import (
                database_transaction_id,
            )

            database_transaction_id.set(shortuuid.uuid())
            result = await func(*args, **kwargs)

            return result
        finally:
            from mini_framework.databases.conn_managers.db_manager import (
                db_connection_manager,
            )

            await db_connection_manager.clear_async_session()

    return inner
