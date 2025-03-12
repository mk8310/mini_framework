import asyncio

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import Session

from mini_framework.databases.config import DatabaseConfig
from mini_framework.databases.conn_managers.load_balancer import LoadBalancer
from mini_framework.databases.conn_managers.utilities import (
    get_db_components,
    database_transaction_id,
)


class TenantDBConnectionManager(object):
    def __init__(
            self, master_db_config: DatabaseConfig, slaves_dbs_config: list[DatabaseConfig]
    ):
        """
        初始化租户数据库连接管理器
        :param master_db_config: 主数据库配置
        :param slaves_dbs_config: 从数据库配置
        """
        self.__session_local = None
        _, _, session, _ = get_db_components()
        self.__async_session_lock = asyncio.Lock()
        self.__sessions: dict[str, dict[str, session]] = dict()
        self.__session_local: dict[str, LoadBalancer] = {
            "master": LoadBalancer([master_db_config])
        }
        if len(slaves_dbs_config) > 0:
            self.__session_local["slave"] = LoadBalancer(slaves_dbs_config)

    async def get_async_session(self, master: bool) -> AsyncSession:
        """
        获取异步会话
        :param master: 是否主库
        :return:
        """
        request_id = database_transaction_id.get()
        flag = "master" if master else "slave"
        if flag not in self.__session_local:
            # 从库配置为空，直接返回主库
            flag = "master"
        async with self.__async_session_lock:
            if request_id not in self.__sessions:
                self.__sessions[request_id] = dict()
                session_factory = self.__session_local[flag].get_session_factory()
                self.__sessions[request_id][flag] = session_factory()
            session_map = self.__sessions[request_id]
            if flag not in session_map:
                session_factory = self.__session_local[flag].get_session_factory()
                session_map[flag] = session_factory()
        return self.__sessions[request_id][flag]

    async def close_async_session(self):
        """
        关闭异步会话
        :return:
        """
        request_id = database_transaction_id.get()
        if request_id is None or request_id not in self.__sessions:
            return
        async with self.__async_session_lock:
            session_map = self.__sessions.pop(request_id, None)
        if not session_map:
            return
        for flag, session in session_map.items():
            try:
                # 检查是否存在未提交的事务
                if session.in_transaction():
                    await session.commit()
            except Exception as e:
                # 记录异常信息
                from mini_framework.utils.log import logger

                logger.exception(e)
                await session.rollback()
            finally:
                await session.close()
                self.__session_local[flag].release_session(session)
        session_map.clear()

    async def exception_close_async_session(self):
        """报错后释放连接到连接池"""

        request_id = database_transaction_id.get()
        if request_id is None or request_id not in self.__sessions:
            return
        async with self.__async_session_lock:
            session_map = self.__sessions.pop(request_id, None)
        if not session_map:
            return
        for flag, session in session_map.items():
            await session.close()
            self.__session_local[flag].release_session(session)

    def get_sync_session(self, master: bool) -> Session:
        """
        获取同步会话
        :param master: 是否主库
        :return:
        """
        request_id = database_transaction_id.get()
        flag = "master" if master else "slave"
        if flag not in self.__session_local:
            # 从库配置为空，直接返回主库
            flag = "master"
        if request_id not in self.__sessions:
            self.__sessions[request_id] = dict()
            session_factory = self.__session_local[flag].get_session_factory()
            self.__sessions[request_id][flag] = session_factory()
        session_map = self.__sessions[request_id]
        if flag not in session_map:
            session_factory = self.__session_local[flag].get_session_factory()
            session_map[flag] = session_factory()
        return self.__sessions[request_id][flag]

    def close_sync_session(self):
        """
        关闭同步会话
        :return:
        """
        request_id = database_transaction_id.get()
        if request_id is None or request_id not in self.__sessions:
            return
        session_map = self.__sessions.pop(request_id, None)
        if not session_map:
            return
        for flag, session in session_map.items():
            try:
                # 检查是否存在未提交的事务
                if session.in_transaction():
                    session.commit()
            except Exception as e:
                # 记录异常信息
                from mini_framework.utils.log import logger

                logger.exception(e)
                session.rollback()
            finally:
                session.close()
                self.__session_local[flag].release_session(session)
        session_map.clear()

    async def dispose_engine(self):
        """
        释放引擎
        :return:
        """
        for session_map in self.__sessions.values():
            for session in session_map.values():
                await session.engine.dispose()
        # self.__sessions.clear()
        # self.__session_local.clear()
        # self.__async_session_lock.release()
        # self.__async_session_lock = None
        # self.__sessions
