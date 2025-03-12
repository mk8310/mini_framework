from typing import Optional, Sequence, Any

from sqlalchemy import event, Executable, util, Result, text
from sqlalchemy.engine.interfaces import _CoreAnyExecuteParams
from sqlalchemy.exc import OperationalError, DisconnectionError
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker
from sqlalchemy.orm import Session, sessionmaker
from sqlalchemy.orm._typing import OrmExecuteOptionsParameter
from sqlalchemy.orm.session import _BindArguments
from tenacity import (
    AsyncRetrying,
    stop_after_attempt,
    wait_exponential,
    retry_if_exception_type,
    retry,
)


class MiniSyncSession(Session):
    def flush(self, objects: Optional[Sequence[Any]] = None) -> None:
        super().flush(objects)
        self.info["flushed"] = True

    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(min=1, max=3),
        retry=retry_if_exception_type((OperationalError, DisconnectionError)),
    )
    def execute(
        self,
        statement: Executable,
        params: Optional[_CoreAnyExecuteParams] = None,
        *,
        execution_options: OrmExecuteOptionsParameter = util.EMPTY_DICT,
        bind_arguments: Optional[_BindArguments] = None,
        _parent_execute_state: Optional[Any] = None,
        _add_event: Optional[Any] = None,
    ) -> Result[Any]:
        result = super().execute(
            statement,
            params,
            execution_options=execution_options,
            bind_arguments=bind_arguments,
            _parent_execute_state=_parent_execute_state,
            _add_event=_add_event,
        )
        self.info["executed"] = True
        return result

    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(min=1, max=3),
        retry=retry_if_exception_type((OperationalError, DisconnectionError)),
    )
    def commit(self) -> None:
        super().commit()
        self.info["committed"] = True


class MiniAsyncSession(AsyncSession):
    async def flush(self, objects: Optional[Sequence[Any]] = None) -> None:
        await super().flush(objects)
        self.info["flushed"] = True

    async def execute(
        self,
        statement: Executable,
        params: Optional[_CoreAnyExecuteParams] = None,
        *,
        execution_options: OrmExecuteOptionsParameter = util.EMPTY_DICT,
        bind_arguments: Optional[_BindArguments] = None,
        _parent_execute_state: Optional[Any] = None,
        _add_event: Optional[Any] = None,
    ) -> Result[Any]:
        result = await super().execute(
            statement,
            params,
            execution_options=execution_options,
            bind_arguments=bind_arguments,
            _parent_execute_state=_parent_execute_state,
            _add_event=_add_event,
        )
        self.info["executed"] = True
        return result

    async def commit(self) -> None:
        async for attempt in AsyncRetrying(
            stop=stop_after_attempt(3),
            wait=wait_exponential(min=1, max=3),
            retry=retry_if_exception_type((OperationalError, DisconnectionError)),
        ):
            with attempt:
                await super().commit()
                self.info["committed"] = True

    async def validate_sql(self, sql_query: str):
        """
        验证 SQL 语句是否合法
        :param sql_query: SQL 语句
        """
        await self.execute(text(f"EXPLAIN {sql_query}"))


# 创建重试策略装饰器
retry_strategy = retry(
    stop=stop_after_attempt(3),
    wait=wait_exponential(min=1, max=2),
    retry=retry_if_exception_type((OperationalError, DisconnectionError)),
)


class SessionMaker(sessionmaker):
    pass


class AsyncSessionMaker(async_sessionmaker):
    pass
