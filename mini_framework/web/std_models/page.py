from typing import List, Type, TypeVar, Generic

from fastapi import Query
from pydantic import Field

from .base_model import BaseViewModel
from ..toolkit.model_utilities import orm_model_to_view_model
from ...databases.queries.pages import Paging

T = TypeVar("T", bound=BaseViewModel)


class PaginatedResponse(BaseViewModel, Generic[T]):
    """
    分页响应模型
    """

    has_next: bool = Field(..., title="是否有下一页", description="是否有下一页")
    has_prev: bool = Field(..., title="是否有上一页", description="是否有上一页")
    page: int = Field(..., title="当前页码", description="当前页码")
    pages: int = Field(..., title="总页数", description="总页数")
    per_page: int = Field(..., title="每页数量", description="每页数量")
    total: int = Field(..., title="总数量", description="总数量")
    items: List[T] = Field(..., title="数据列表", description="数据列表")

    @classmethod
    def from_paging(
        cls, paging: Paging, model: Type[T], other_mapper: dict[str, str] = None
    ):
        result_items = []
        for item in paging.items:
            inst = orm_model_to_view_model(item, model, other_mapper)
            result_items.append(inst)
        return cls(
            has_next=paging.has_next,
            has_prev=paging.has_prev,
            page=paging.page,
            pages=paging.page_count,
            per_page=paging.page_size,
            total=paging.total,
            items=result_items,
        )

    class Config:
        json_schema_extra = {
            "example": {
                "has_next": True,
                "has_prev": False,
                "page": 1,
                "pages": 1,
                "per_page": 10,
                "total": 1,
                "items": [],
            }
        }


class PageRequest(BaseViewModel):
    """
    分页请求模型
    """

    page: int = Query(1, title="页码", description="页码")
    per_page: int = Query(10, title="每页数量", ge=1, description="每页数量")

    class Config:
        from_attributes = True
        json_schema_extra = {"example": {"page": 1, "per_page": 10}}
