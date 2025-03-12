from abc import ABC, abstractmethod
from math import ceil
from typing import List, Callable

from ..entities import to_dicts


class Pagination(object):
    """Internal helper class returned by :meth:`BaseQuery.paginate`.  You
    can also construct it from any other SQLAlchemy query object if you are
    working with other libraries.  Additionally it is possible to pass `None`
    as query object in which case the :meth:`prev` and :meth:`next` will
    no longer work.
    """

    def __init__(self, page, per_page, total):
        #: the unlimited query object that was used to create this
        #: pagination object.
        #: the current page number (1 indexed)
        self.page = page
        #: the number of items to be displayed on a page.
        self.per_page = per_page
        #: the total number of items matching the query
        self.total = total
        #: the items for the current page
        # self.items = items

    @property
    def pages(self):
        """The total number of pages"""
        if self.per_page == 0:
            pages = 0
        else:
            pages = int(ceil(self.total / float(self.per_page)))
        return pages

    @property
    def prev_num(self):
        """Number of the previous page."""
        if not self.has_prev:
            return None
        return self.page - 1

    @property
    def has_prev(self):
        """True if a previous page exists"""
        return self.page > 1

    @property
    def has_next(self):
        """True if a next page exists."""
        return self.page < self.pages

    @property
    def next_num(self):
        """Number of the next page"""
        if not self.has_next:
            return None
        return self.page + 1

    def iter_pages(self, left_edge=2, left_current=2,
                   right_current=5, right_edge=2):
        last = 0
        for num in range(1, self.pages + 1):
            page_num = self.page - left_current - 1 < num < self.page + right_current
            if num <= left_edge or page_num or num > self.pages - right_edge:
                if last + 1 != num:
                    yield None
                yield num
                last = num


class PagingItemsSerializer(ABC):
    @abstractmethod
    def to_dicts(self, items):
        pass


class Paging(object):
    has_next = False
    has_prev = False
    page = 1
    page_count = 1
    page_size = 20
    total = 1

    def __init__(self, db_paging: Pagination, items: List):
        self.has_next: bool = db_paging.has_next  # 是否有下一页
        self.has_prev: bool = db_paging.has_prev  # 是否有上一页
        self.page: int = db_paging.page  # 当前页页码
        self.page_count: int = db_paging.pages  # 总页数
        self.page_size: int = db_paging.per_page  # 单页记录数
        self.total: int = db_paging.total  # 总记录数
        self.items: List = items  # 记录列表
        self.items_to_dict: Callable = to_dicts
        self.to_dicts_kwargs: dict = dict()

    def set_serialize_func(self, to_dicts_func: Callable, **kwargs):
        self.items_to_dict = to_dicts_func
        self.to_dicts_kwargs.update(**kwargs)

    @property
    def items_dict(self):
        if len(self.items) > 0:
            item_list_dict = self.items_to_dict(self.items, **self.to_dicts_kwargs)
            return item_list_dict
        return []

    @property
    def page_info_dict(self):
        page = self.page
        page_size = self.page_size
        total = self.total
        page_count = self.page_count
        return dict(
            total=total,
            page_count=int(page_count),
            current_page=page,
            page_size=page_size,
            has_next=self.has_next,
            has_prev=self.has_prev
        )

    def to_dict(self):
        result = dict(
            has_next=self.has_next,
            has_prev=self.has_prev,
            page=self.page,
            pages=self.page_count,
            per_page=self.page_size,
            total=self.total,
            items=self.items_to_dict(self.items, **self.to_dicts_kwargs)
        )
        return result
