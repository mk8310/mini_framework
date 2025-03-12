from contextvars import ContextVar
from typing import Optional

from mini_framework.context import env

# 数据库事务ID
database_transaction_id: ContextVar[Optional[str]] = ContextVar(
    "database_transaction_id", default=None
)


def get_db_components():
    if env.sync_type == "sync":
        from .sessions import MiniSyncSession, SessionMaker
        from sqlalchemy import create_engine
        from sqlalchemy.orm import scoped_session

        return create_engine, SessionMaker, MiniSyncSession, scoped_session
    else:
        from .sessions import MiniAsyncSession, AsyncSessionMaker
        from sqlalchemy.ext.asyncio import (
            async_scoped_session,
            create_async_engine,
        )

        return (
            create_async_engine,
            AsyncSessionMaker,
            MiniAsyncSession,
            async_scoped_session,
        )


def scoped_session_func():
    return database_transaction_id.get()


def create_db_session_factory(db):
    """
    创建数据库会话工厂
    :param db: 数据库配置
    :return: 数据库会话工厂
    """
    create_engine_func, session_maker_func, session_cls, scoped_session = (
        get_db_components()
    )
    extra_params = db.extra if db.extra else {}
    db_uri = db.sync_database_uri if env.sync_type == "sync" else db.async_database_uri
    # 数据库引擎
    slave_engine = create_engine_func(
        db_uri,
        echo=env.debug,
        pool_size=db.pool_size,
        max_overflow=db.max_overflow,
        pool_timeout=db.pool_timeout,
        pool_recycle=db.pool_recycle,
        pool_pre_ping=db.pool_pre_ping,
        **extra_params
    )
    # 创建会话工厂
    local_session = session_maker_func(
        autocommit=False, autoflush=False, bind=slave_engine, class_=session_cls
    )
    return scoped_session(local_session, scopefunc=scoped_session_func)
