from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import Session
from mini_framework.design_patterns.singleton import singleton


@singleton
class DBConnectionManager:

    def __init__(self):
        from mini_framework.databases.config import db_config
        from mini_framework.databases.conn_managers.tenant_db import (
            TenantDBConnectionManager,
        )

        self.tenants: dict[str, TenantDBConnectionManager] = dict()
        for key, db_cluster in db_config.databases.items():
            self.tenants[key] = TenantDBConnectionManager(
                db_cluster.master, db_cluster.slaves
            )

    async def get_async_session(self, db_key: str, master: bool) -> AsyncSession:
        """
        获取异步会话
        :param db_key: 数据库唯一标识
        :param master: 是否主库
        :return:
        """
        session = await self.tenants[db_key].get_async_session(master)
        return session

    async def clear_async_session(self, all_down: bool = False):
        """
        清除异步会话
        :param all_down: 是否关闭所有连接
        :return:
        """
        for tenant in self.tenants.values():
            await tenant.close_async_session()
            if all_down:
                await tenant.dispose_engine()

    async def exception_clear_async_session(self):
        """
        报错后清除异步会话
        """
        for tenant in self.tenants.values():
            await tenant.exception_close_async_session()

    def get_sync_session(self, db_key: str, master: bool) -> Session:
        """
        获取同步会话
        :param db_key: 数据库唯一标识
        :param master: 是否主库
        :return:
        """
        return self.tenants[db_key].get_sync_session(master)

    def clear_sync_session(self):
        for tenant in self.tenants.values():
            tenant.close_sync_session()


db_connection_manager = DBConnectionManager()
