import time
from contextvars import ContextVar
from typing import Dict, Optional, Any

import shortuuid
from fastapi.requests import Request
from starlette.datastructures import URL

from mini_framework.design_patterns.depend_inject import get_injector
from mini_framework.design_patterns.singleton import singleton
from mini_framework.web.std_models.account import RenderAccount, AccountInfo

current_request_id: ContextVar[Optional[str]] = ContextVar(
    "current_request_id", default=None
)


class RequestContext:
    def __init__(self, request: Request, request_id: str):
        """
        Web 请求上下文
        :param request: Web 请求对象
        """
        self.__request: Request = request
        self.__data: dict[str, Any] = {"request_id": request_id}

    def __getitem__(self, key):
        return self.__data[key]

    def __setitem__(self, key, value):
        self.__data[key] = value

    def __contains__(self, key):
        return key in self.__data

    def __delitem__(self, key):
        del self.__data[key]

    def __iter__(self):
        return iter(self.__data)

    def __len__(self):
        return len(self.__data)

    def __repr__(self):
        return repr(self.__data)

    def __str__(self):
        return str(self.__data)

    @property
    def start_time(self) -> float:
        return self.__data["start_time"]

    @start_time.setter
    def start_time(self, value: float):
        self.__data["start_time"] = value

    @property
    def url(self) -> URL:
        return self.__request.url

    @property
    def request_id(self):
        return self.__data["request_id"]

    @request_id.setter
    def request_id(self, value):
        self.__data["request_id"] = value

    @property
    def session_id(self):
        return self.__data["session_id"]

    @session_id.setter
    def session_id(self, value):
        self.__data["session_id"] = value

    @property
    def token(self) -> str:
        return self.__data.get("token", "")

    @token.setter
    def token(self, value: str):
        self.__data["token"] = value

    @property
    def end_time(self) -> float:
        return self.__data.get("end_time", 0)

    @end_time.setter
    def end_time(self, value: float):
        self.__data["end_time"] = value

    @property
    def duration(self) -> float:
        return self.end_time - self.start_time

    @property
    def tenant_code(self):
        return self.__data.get("tenant_code")

    @property
    def request(self):
        return self.__request

    @property
    def current_login_account(self) -> RenderAccount:
        account_info = self.__data.get("current_user")
        return account_info

    @current_login_account.setter
    def current_login_account(self, value: RenderAccount):
        self.__data["current_user"] = value

    async def get_full_account_info(self) -> AccountInfo:
        current_login_account = self.current_login_account
        from mini_framework.authentication.rules.auth_rule import AuthRules

        auth_rule: AuthRules = get_injector(AuthRules)
        account_info = await auth_rule.get_account_by_id(
            current_login_account.account_id
        )
        return account_info

    @property
    def ip_chain(self):
        """
        获取 IP 链
        :return:
        """
        x_forwarded_for = self.request.headers.get("X-Forwarded-For")
        x_real_ip = self.request.headers.get("X-Real-IP")

        ip_chain = x_forwarded_for or x_real_ip or self.request.client.host
        if ip_chain:
            return ip_chain.split(",")
        return []

    @property
    def real_ip(self):
        """
        获取真实客户端 IP，需要考虑反向代理的情况
        :return:
        """
        # 获取客户端IP
        client_ip = self.request.client.host

        # 获取反向代理IP
        ip_chain = self.ip_chain
        if ip_chain:
            return ip_chain[0].strip()
        return client_ip


@singleton
class RequestContextManager:
    def __init__(self):
        """
        Web 请求上下文管理器
        """
        self.request_contexts: Dict[str, RequestContext] = {}

    def get(self, request: Request):
        if not current_request_id.get():
            request_context = self.__create(request)
        else:
            request_context = self.request_contexts[current_request_id.get()]
        return request_context

    def remove(self, request_id: str):
        self.request_contexts.pop(request_id, None)

    def __create(self, request: Request):
        request_id = shortuuid.uuid()
        request_context = RequestContext(request, request_id)
        tenant_code = request.headers.get("x-tenant-code", None)
        if tenant_code:
            request_context["tenant_code"] = tenant_code

        session_id = request.headers.get("x-request-session-id", None)
        if not session_id:
            session_id = shortuuid.uuid()
        request_context.session_id = session_id

        request_context.start_time = time.time()
        self.request_contexts[request_id] = request_context
        return request_context

    def current(self) -> RequestContext:
        """
        获取当前请求上下文
        :return: 请求上下文
        """
        request_id = current_request_id.get()
        return self.request_contexts.get(request_id)


request_context_manager = RequestContextManager()
