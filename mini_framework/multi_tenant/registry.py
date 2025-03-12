from __future__ import annotations

from typing import Callable

from injector import singleton

from .errors import TenantNotFoundError
from .tenant import Tenant, TenantStatus
from ..design_patterns.depend_inject import get_injector
from ..utils.lru_cache import async_lru_cache


@singleton
class TenantRegistry:
    """
    租户信息注册表
    """

    def __init__(self):
        self.__tenants: dict[str, Tenant] = {}
        self.__get_tenant: callable = None

    def register_get_tenant(self, get_tenant_func: Callable[[str], Tenant]):
        """
        注册获取租户信息的方法
        :param get_tenant_func: 获取租户信息的方法, 该方法接收租户编码，返回租户信息
        """
        self.__get_tenant = get_tenant_func

    async def __invoke_get_tenant(self, code: str) -> Tenant | None:
        """
        调用获取租户信息的方法
        :param code: 租户编码
        :return: 租户信息
        """
        if self.__get_tenant:
            return await self.__get_tenant(code)
        return None

    @async_lru_cache(maxsize=1024)
    async def get_tenant(self, code: str) -> Tenant | None:
        """
        获取租户信息
        :param code: 租户编码
        :return: 租户信息
        :raises TenantNotFoundError: 租户不存在
        """
        if not code:
            return None
        tenant = None
        # if code in self.__tenants:
        #     tenant = await self.__get_tenant_from_cache(code)
        if tenant is None:
            tenant = await self.__invoke_get_tenant(code)
        if tenant is not None:
            self.__tenants[code] = tenant
            return tenant
        raise TenantNotFoundError(f"Tenant {code} not found.")

    def tenant_expire(self, code: str):
        """
        租户过期
        :param code: 租户编码
        """
        tenant = self.__tenants.get(code)
        if tenant is not None:
            tenant.status = TenantStatus.expired
            self.__tenants[code] = tenant


tenant_registry: TenantRegistry = get_injector(TenantRegistry)
