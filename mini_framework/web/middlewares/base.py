from __future__ import annotations

import time
from abc import abstractmethod, ABC
from typing import List, Optional, Type

from fastapi import HTTPException, FastAPI
from fastapi.exceptions import RequestValidationError
from pydantic import ValidationError
from starlette.middleware.base import BaseHTTPMiddleware, DispatchFunction
from starlette.requests import Request
from starlette.responses import Response
from starlette.types import ASGIApp

from mini_framework.design_patterns.singleton import singleton
from mini_framework.web.request_context import request_context_manager, RequestContext, current_request_id
from mini_framework.web.std_models.errors import MiniHTTPException


class ResponseManager(object):
    def __init__(self, request_context: RequestContext, response: Optional[Response, Exception]):
        """
        响应管理器
        :param request_context: 请求上下文
        """
        self._request_context = request_context
        self._response: Optional[Response, Exception] = response

    def __make_headers(self, headers):
        from mini_framework.web.mini_app import app_config
        self._request_context.end_time = time.time()
        headers["x-request-start-time"] = str(self._request_context.start_time)
        headers["x-request-end-time"] = str(self._request_context.end_time)
        headers["x-request-id"] = self._request_context.request_id
        headers["x-request-version"] = app_config.version
        headers["x-request-cost-time"] = str(self._request_context.duration)
        headers["x-request-app"] = app_config.name
        headers["x-request-session-id"] = self._request_context.session_id
        if self._request_context.token is not None and self._request_context.token != "":
            token = f"Bearer {self._request_context.token}"
            headers["Authorization"] = token
        return headers

    async def response(self):
        response_or_error = self._response
        if isinstance(response_or_error, Response):
            self.__make_headers(response_or_error.headers)
            return response_or_error
        elif isinstance(response_or_error, MiniHTTPException):
            headers = self.__make_headers({})
            response = response_or_error.response(headers)
            return response
        else:
            headers = self.__make_headers({})
            response_or_error = MiniHTTPException.from_exception(response_or_error, headers)
            response = response_or_error.response()

            # 临时方案：Exception后释放数据连接
            from mini_framework.databases.conn_managers.db_manager import (
                db_connection_manager,
            )
            await db_connection_manager.exception_clear_async_session()
            return response


class MiddlewareBase(ABC):
    def __init__(self):
        """
        中间件基类
        """
        pass

    @abstractmethod
    def initialize(self, app: ASGIApp):
        pass

    @abstractmethod
    async def before_request(self, request: RequestContext):
        pass

    @abstractmethod
    async def after_request(self, request: RequestContext, response_manager: ResponseManager):
        pass


@singleton
class MiddlewareManager(object):
    def __init__(self):
        """
        中间件管理器
        """
        self._middlewares: List[MiddlewareBase] = []

    def register(self, middleware: Type[MiddlewareBase]):
        self._middlewares.append(middleware())

    @property
    def middlewares(self):
        for middleware in self._middlewares:
            yield middleware


middleware_manager = MiddlewareManager()


class RequestProcessMiddleware(BaseHTTPMiddleware):
    """
    请求过程中间件
    """

    def __init__(self, app: ASGIApp, dispatch: DispatchFunction | None = None) -> None:
        super(RequestProcessMiddleware, self).__init__(app, dispatch)
        for middleware in middleware_manager.middlewares:
            middleware.initialize(app)

    async def dispatch(self, request: Request, call_next):
        request_context = request_context_manager.get(request)
        current_request_id.set(request_context.request_id)
        for middleware in middleware_manager.middlewares:
            await middleware.before_request(request_context)

        response = await call_next(request)
        response_manager = ResponseManager(request_context, response)

        for middleware in middleware_manager.middlewares:
            await middleware.after_request(request_context, response_manager)

        response = await response_manager.response()

        request_context_manager.remove(request_context.request_id)

        return response


class HandlerRegister:
    def __init__(self, app: FastAPI):
        self._app = app

    def register(self):
        self._app.exception_handler(MiniHTTPException)(self.std_http_error_handler)
        self._app.exception_handler(RequestValidationError)(self.validation_exception_handler)
        self._app.exception_handler(ValidationError)(self.validation_exception_handler)
        self._app.exception_handler(HTTPException)(self.http_exception_handler)
        self._app.exception_handler(Exception)(self.std_http_error_handler)

    async def std_http_error_handler(self, request, exc: MiniHTTPException):
        return await self.__render_error_response(exc, request)

    async def validation_exception_handler(self, request, exc: ValidationError):
        exc = MiniHTTPException.from_validation_error(exc)
        return await self.__render_error_response(exc, request)

    async def http_exception_handler(self, request, exc: HTTPException):
        exc = MiniHTTPException.from_http_exception(exc)
        return await self.__render_error_response(exc, request)

    async def exception_handler(self, request, exc: Exception):
        exc = MiniHTTPException.from_exception(exc)
        return await self.__render_error_response(exc, request)

    async def __render_error_response(self, exc, request):
        request_context = request_context_manager.get(request)
        response_manager = ResponseManager(request_context, exc)
        return await response_manager.response()
