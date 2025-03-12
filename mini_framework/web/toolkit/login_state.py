from mini_framework.authentication.jwt import jwt_utils
from mini_framework.cache.manager import redis_client_manager
from mini_framework.design_patterns.singleton import singleton

UNIQUE_KEY = "unique_key"


@singleton
class LoginStateManager:
    """
    登录用户信息管理
    """

    def __init__(self):
        self.__login_state_cache = redis_client_manager.get_client("login_state")
        self.__tenant = None

    def set_tenant(self, tenant):
        """
        设置租户信息
        :param tenant: 租户信息
        :return:
        """
        self.__tenant = tenant

    async def issue(self, unique_id: str) -> str:
        """
        颁发 token
        :param unique_id: 用户唯一标识
        :return:
        """
        return jwt_utils.issue({UNIQUE_KEY: unique_id})

    async def verify_token(self, token: str) -> dict:
        """
        验证 token
        :param token: token
        :return:
        """
        client_id = self.__tenant.client_id if self.__tenant else None
        cert = None if self.__tenant is None else self.__tenant.cert_content
        return await jwt_utils.verify(token, client_id, cert=cert)

    async def revoke_token(self, token: str):
        """
        撤销 token
        :param token: token
        :return:
        """
        client_id = self.__tenant.client_id if self.__tenant else None
        cert = None if self.__tenant is None else self.__tenant.cert_content
        payload = await jwt_utils.verify(token, client_id, cert=cert)
        self.__login_state_cache.delete(payload.get(UNIQUE_KEY))


login_state_manager = LoginStateManager()
