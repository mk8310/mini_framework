from typing import Callable, Type, List, Tuple

from pydantic import create_model

from mini_framework.utils.func_inspect import Function
from mini_framework.web.request_context import (
    request_context_manager,
    RequestContextManager,
)
from mini_framework.web.session import Session
from mini_framework.web.std_models.base_model import BaseViewModel


def create_route_handler(view_cls: Type, method_name: str) -> Tuple[Callable, Function]:
    method = getattr(view_cls, method_name)
    func = Function(method)

    async def route_handler(*args, **kwargs):
        view_instance = view_cls()
        bound = func.signature.bind(view_instance, *args, **kwargs)
        bound.apply_defaults()
        return await method(*bound.args, **bound.kwargs)

    # 动态设置函数签名，以便 Swagger 文档正确生成
    new_sig = func.signature.replace(
        parameters=func.parameters_without_self.values(),
        return_annotation=func.return_annotation,
    )
    route_handler.__signature__ = new_sig
    return route_handler, func


def create_paginated_response_model(
    item_type: Type[BaseViewModel],
) -> Type[BaseViewModel]:
    type_name = f"PaginatedResponse_{item_type.__name__}"
    fields = {"items": (List[item_type], ...)}
    from mini_framework.web.std_models.page import PaginatedResponse

    model = create_model(type_name, __base__=PaginatedResponse, **fields)
    return model


def get_response_cls(method_name, response_cls, func: Function):
    """
    获取响应模型
    :param method_name: 方法名
    :param response_cls: 响应模型
    :param func: 函数对象
    :return:
    """
    if func.return_annotation_can_serialize():
        return func.return_annotation
    response_model = None
    if method_name == "get" and response_cls:
        response_model = response_cls
    elif method_name == "query" and response_cls:
        response_model = List[response_cls]
    elif method_name == "page" and response_cls:
        response_model = create_paginated_response_model(response_cls)
    elif method_name == "post" and response_cls:
        response_model = response_cls
    elif method_name == "put" and response_cls:
        response_model = response_cls
    elif method_name == "delete" and response_cls:
        response_model = int
    return response_model


class BaseView:
    def __init__(self):
        self.request_context_manager: RequestContextManager = request_context_manager

    @property
    def session(self) -> Session:
        return Session(self.request_context_manager.current().session_id)

    @staticmethod
    def register_routes(cls, path: str, response_cls, description: str = None):
        methods = [
            "get",
            "query",
            "page",
            "post",
            "put",
            "delete",
            "options",
            "head",
            "patch",
            "trace",
        ]
        method_describes = {
            "get": "单个获取",
            "query": "查询列表",
            "page": "分页查询",
            "post": "新增",
            "put": "修改",
            "delete": "删除",
            "options": "OPTIONS",
            "head": "HEAD",
            "patch": "PATCH",
        }
        cls_methods = [
            attr_name
            for attr_name in dir(cls)
            if callable(getattr(cls, attr_name)) and not attr_name.startswith("_")
        ]
        routers = []
        for cls_method in cls_methods:
            split_name = cls_method.split("_", 1)
            method_name = split_name[0]
            if method_name not in methods:
                continue
            method_suffix = ""
            if method_name in ["page", "query"]:
                method_suffix = method_name
            method_name = "get" if method_name in ["page", "query"] else method_name
            if len(split_name) == 2:
                method_suffix = split_name[1].replace("_", "-")
            method_describes[method_name] = method_describes.get(
                split_name[0], method_suffix
            )
            real_method = method_name
            real_path = f"{path}/{method_suffix}"
            handler, func = create_route_handler(cls, cls_method)
            real_summary = func.summary.title if func.summary else None
            real_description = (
                f"{description} - {method_describes[method_name]}"
                if not func.summary
                else func.summary.description
            )
            response_model = get_response_cls(split_name[0], response_cls, func)
            routers.append(
                dict(
                    path=real_path,
                    endpoint=handler,
                    methods=[real_method.upper()],
                    tags=[description or cls.__name__],
                    response_model=response_model,
                    summary=real_summary,
                    description=real_description,
                    response_description=(
                        func.return_doc.description if func.return_doc else None
                    ),
                )
            )
        return routers
