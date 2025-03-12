from typing import Callable

from sqlalchemy import select, func, update
from sqlalchemy.ext.asyncio import AsyncSession


from mini_framework.databases.entities import BaseDBModel
from mini_framework.databases.queries.pages import Pagination, Paging
from mini_framework.web.std_models.page import PageRequest


def get_update_contents(model_inst: BaseDBModel, *args) -> dict:
    kwargs = {}
    for arg in args:
        kwargs[arg] = getattr(model_inst, arg)
    return kwargs


def _get_db_model_primary_keys(model_inst: BaseDBModel):
    primary_keys = []
    for key in model_inst.__table__.primary_key.columns.keys():
        primary_keys.append(getattr(model_inst, key))
    return primary_keys


class DAOBase:
    def __init__(self):
        from mini_framework.databases.conn_managers.db_manager import (
            db_connection_manager,
        )

        self.__db = db_connection_manager
        self.__db_key = "default"

    @property
    def db(self):
        return self.__db

    async def master_db(self, db_key: str = None) -> AsyncSession:
        """
        获取主库session
        :param db_key: 数据库key
        :return:
        """
        db_key = db_key if db_key else self.__db_key
        return await self.db.get_async_session(db_key, True)

    async def slave_db(self, db_key: str = None) -> AsyncSession:
        """
        获取从库session
        :param db_key: 数据库key
        :return:
        """
        db_key = db_key if db_key else self.__db_key
        return await self.db.get_async_session(db_key, False)

    async def update(
        self,
        session,
        update_stmt,
        model_inst: BaseDBModel,
        update_values: dict,
        is_commit: bool = False,
    ):
        await session.execute(update_stmt)
        for key, value in update_values.items():
            setattr(model_inst, key, value)
        return model_inst

    async def delete(self, session, model_inst: BaseDBModel, is_commit: bool = False):
        if not model_inst:
            return None
        deleted_flag = "is_deleted"
        if deleted_flag not in model_inst.__dict__:
            return await self.__physical_delete(model_inst, is_commit)
        model_inst.is_deleted = True
        update_values = dict(is_deleted=True)
        primary_keys = _get_db_model_primary_keys(model_inst)
        update_stmt = update(model_inst.__class__)
        # 根据primary_keys生成where条件
        for index, primary_key in enumerate(primary_keys):
            update_stmt = update_stmt.where(
                # model_inst.__class__.__table__.primary_key.columns.keys()[index] == primary_key
                getattr(
                    model_inst.__class__,
                    model_inst.__class__.__table__.primary_key.columns.keys()[index],
                )
                == primary_key
            )
        update_stmt = update_stmt.values(is_deleted=True)
        # update_stmt = update(model_inst.__class__) \
        #     .where(model_inst.__class__.id == model_inst.id) \
        #     .values(is_deleted=True)
        return await self.update(
            session, update_stmt, model_inst, update_values, is_commit=is_commit
        )

    async def __physical_delete(self, model_inst, is_commit):
        session = await self.master_db()
        await session.delete(model_inst)
        return model_inst

    async def validate_sql(self, db_key: str, sql_query: str):
        """
        验证 SQL 语句是否合法
        :param db_key: 数据库key
        :param sql_query: SQL 语句
        """
        session = await self.master_db(db_key)
        await session.validate_sql(sql_query)

    async def query_page(
        self, query, page_request: PageRequest, to_dicts_func: Callable = None
    ) -> Paging:
        """
        通用分页查询方法。

        Args:
            query (sqlalchemy.sql.selectable.Select): 未执行的查询对象。
            page_request (PageRequest): 分页请求对象，包含页码和每页记录数。
            to_dicts_func (Callable): 可选，将结果转换为字典的函数。

        Returns:
            Paging: 包含分页信息和当前页数据的对象。
        """
        # 首先，计算总记录数
        session = await self.slave_db()
        column_names = query.columns.keys()
        count_query = select(func.count()).select_from(query.subquery())
        result_count = await session.execute(count_query)
        total_items = result_count.scalar()

        # 计算需要跳过的记录数
        offset = (page_request.page - 1) * page_request.per_page

        # 执行查询，获取当前页的数据
        result_list = await session.execute(
            query.offset(offset).limit(page_request.per_page)
        )
        result_items = list(result_list.fetchall())
        items = []
        for item in result_items:
            if issubclass(item[0].__class__, BaseDBModel):
                items.append(item[0])
            else:
                item_dict = dict(zip(column_names, item))
                items.append(item_dict)

        # 创建Pagination对象
        pagination = Pagination(page_request.page, page_request.per_page, total_items)

        # 使用自定义的to_dicts_func，如果提供
        if to_dicts_func:
            items = to_dicts_func(items)

        # 创建并返回Paging对象
        paging = Paging(pagination, items)
        return paging
