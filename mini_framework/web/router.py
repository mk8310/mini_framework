from datetime import datetime
from typing import Type, List, Callable

from fastapi import APIRouter

from mini_framework.design_patterns.singleton import singleton
from mini_framework.web.std_models.base_model import BaseViewModel
from mini_framework.web.views import BaseView


def health_check():
    from mini_framework.web.mini_app import app_config

    return dict(
        name=app_config.name,
        version=app_config.version,
        description=app_config.description,
        author="Mini technical",
        author_email="cloud@mini.cn",
        copyright=f"Copyright © {datetime.now().year} Mini technical",
    )


class Router:
    def __init__(self, require_auth: bool = True):
        self._root_router = APIRouter()
        self.__need_login = require_auth
        self._routers: List[Router] = []

    @property
    def require_auth(self):
        return self.__need_login

    def set_root_prefix(self, prefix):
        self._root_router.prefix = prefix

    def include_router(self, router):
        self._routers.append(router)

    def include_api_view(self, api_view):
        api_view.register(self)

    def register_func_router(
        self,
        func: Callable,
        path: str,
        methods: list[str],
        response_cls=None,
        description: str = None,
        show_in_doc: bool = True,
    ):
        func.require_auth = self.require_auth
        self._root_router.add_api_route(
            path,
            func,
            methods=methods,
            response_model=response_cls,
            description=description,
            include_in_schema=show_in_doc,
        )

    # api_view_class 必须是 BaseView 的子类
    def include_api_view_class(
        self,
        api_view_class: Type[BaseView],
        path: str,
        sub_api_router: APIRouter = None,
        response_cls=None,
        description: str = None,
    ):
        if not issubclass(api_view_class, BaseView):
            raise ValueError("api_view_class 必须是 BaseView 的子类")
        if response_cls and not issubclass(response_cls, BaseViewModel):
            raise ValueError("model_class 必须是 BaseViewModel 的子类")
        sub_routers = BaseView.register_routes(
            api_view_class, path, response_cls, description
        )
        for sub_router in sub_routers:
            sub_router["endpoint"].require_auth = self.require_auth
            if sub_api_router:
                sub_api_router.add_api_route(**sub_router)
            else:
                self._root_router.add_api_route(**sub_router)

    def get_router(self):
        for sub_router in self._routers:
            self._root_router.include_router(sub_router.get_router())
        return self._root_router


@singleton
class RootRouter(Router):
    def __init__(self):
        super().__init__()
        auth_router = Router(require_auth=False)
        from mini_framework.web.middlewares.auth import (
            auth_callback_api,
            auth_callback_debug,
            auth_tenant_callback_debug,
            auth_login_out,
        )

        auth_router.register_func_router(auth_callback_api, "/auth/callback", ["POST"])
        auth_router.register_func_router(auth_login_out, "/auth/login_out", ["GET"])

        from mini_framework.context import env

        if env.debug:
            auth_router.register_func_router(
                auth_callback_debug,
                "/auth/callback/debug",
                ["GET"],
            )
            auth_router.register_func_router(
                auth_tenant_callback_debug,
                "/auth/tenant/callback/{tenant}/debug",
                ["GET"],
            )

        health_router = Router(require_auth=False)
        health_router.register_func_router(health_check, "/health", ["GET"])

        doc_router = Router(require_auth=False)
        from mini_framework.web.api_doc_manager import docs, redoc

        doc_router.register_func_router(
            docs, "/docs", ["GET", "HEAD"], show_in_doc=False
        )
        doc_router.register_func_router(
            redoc, "/re/docs", ["GET", "HEAD"], show_in_doc=False
        )

        self.include_router(auth_router)
        self.include_router(health_router)
        self.include_router(doc_router)


root_router = RootRouter()
