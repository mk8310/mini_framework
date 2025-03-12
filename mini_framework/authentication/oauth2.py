import base64
import hashlib
import secrets
from urllib.parse import urlencode

from mini_framework.authentication.config import authentication_config
from mini_framework.authentication.jwt import jwt_utils
from mini_framework.utils.http import http_request
from .tenant_auth import TenantAuthorizationInfo
from ..cache.manager import redis_client_manager
from ..multi_tenant.tenant import Tenant


def generate_code_verifier():
    """生成高熵的随机字符串作为code_verifier"""
    return secrets.token_urlsafe(64)


def generate_code_challenge(code_verifier):
    """使用SHA256算法对code_verifier进行哈希，然后进行base64编码，得到code_challenge"""
    sha256 = hashlib.sha256()
    sha256.update(code_verifier.encode("utf-8"))
    return base64.urlsafe_b64encode(sha256.digest()).decode("utf-8").rstrip("=")


class OAuth2Client:
    def __init__(self, tenant: Tenant = None):
        self.__oauth2_config = authentication_config.oauth2
        self.__tenant = tenant
        self.__cache = redis_client_manager.get_client("login_state")

    def get_authorization_url(self, refer_uri: str = "", domain: str = "") -> str:
        """
        获取授权地址
        :param domain: 当前系统域名
        :param state: 随机字符串
        :param refer_uri: 回调地址
        :return: 授权地址
        """
        from urllib.parse import urlencode, quote

        tenant_auth_info = TenantAuthorizationInfo(self.__tenant)
        # code_verifier = generate_code_verifier()
        # code_challenge = generate_code_challenge(code_verifier)
        state = secrets.token_urlsafe(16)
        # self.__cache.set(state, code_verifier, ex=600)

        if not refer_uri:
            refer_uri = tenant_auth_info.home_url
        # refer_uri = urlencode(dict(refer_url=refer_uri))

        redirect_uri = tenant_auth_info.get_redirect_url(refer_uri)
        # f"{tenant_auth_info.get_redirect_url()}?{refer_uri}"
        auth_parameters = urlencode(
            {
                "client_id": tenant_auth_info.client_id,
                "redirect_uri": redirect_uri,
                "grant_type": self.__oauth2_config.grant_type,
                "response_type": "code",
                # 'scope': self.__oauth2_config.scope,
                "state": state,
                # "code_challenge_method": "S256",
                # "code_challenge": code_challenge,
            }
        )
        return f"{self.__oauth2_config.authorization_url}?{auth_parameters}"

    async def get_access_token(self, code: str, state: str) -> str:
        """
        获取访问令牌
        :param state: 随机字符串
        :param code: 授权码
        :return: 访问令牌
        """
        tenant_auth_info = TenantAuthorizationInfo(self.__tenant)
        # code_verifier = self.__cache.get(state)
        token_parameters = {
            "client_id": tenant_auth_info.client_id,
            "client_secret": tenant_auth_info.client_secret,
            "code": code,
            # "code_verifier": code_verifier,
            "redirect_uri": tenant_auth_info.get_redirect_url(),
            "grant_type": "authorization_code",
        }
        resp_json: dict = await http_request.post_json(
            self.__oauth2_config.token_url,
            data=token_parameters,
            headers={"Content-Type": "application/json"},
        )
        access_token = resp_json.get("access_token")
        return access_token

    async def get_account_info(self, access_token: str, has_roles: bool = False) -> dict:
        """
        获取用户信息
        :param access_token: 访问令牌
        :return: 用户信息
        """
        result = jwt_utils.get_payload(access_token)
        if has_roles:
            token_parameters = {
                "access_token": access_token,
            }
            get_url = http_request.build_url(self.__oauth2_config.user_info_url, token_parameters)
            resp_json: dict = await http_request.get_json(
                get_url,
                headers={"Content-Type": "application/json"},
            )
            if resp_json.get("status", "") == 'ok':
                user_id = resp_json.get("sub")
                if user_id == result.get('id'):
                    result['roles'] = resp_json.get('roles', [])
                    result['permissions'] = resp_json.get('policies', [])
                pass
            """
            resp_json:
            Status:      "ok",
            Sub:         user.Id,
            Name:        user.Name,
            Data:        user,
            Data2:       organization,
            Roles:       (roles),
            Policies:    (policies),
            RedirectUri: redirectUrl,
            """

        return result

    async def destroy_token(self, access_token: str) -> dict:
        """
        :param access_token: 访问令牌
        """
        result = await jwt_utils.destroy(access_token)
        await self.request_login_out_token(access_token)

        return result

    async def refresh_access_token(self, refresh_token: str) -> str:
        """
        刷新访问令牌
        :param refresh_token: 刷新令牌
        :return: 访问令牌
        """
        token_parameters = {
            "client_id": self.__oauth2_config.client_id,
            "client_secret": self.__oauth2_config.client_secret,
            "refresh_token": refresh_token,
            "grant_type": "refresh_token",
        }
        resp_json: dict = await http_request.post_json(
            self.__oauth2_config.token_url,
            data=token_parameters,
            headers={"Content-Type": "application/x-www-form-urlencoded"},
        )
        access_token = resp_json.get("access_token")
        return access_token

    async def request_login_out_token(self, refresh_token: str) -> str:
        """
        请求组织中心 销毁 访问令牌
        :param refresh_token: 令牌
        :return: 访问令牌
        """
        token_parameters = {
            "state": "application-center",
            "post_logout_redirect_uri": "",  # 如果是要跳转 传入要跳的url
            "id_token_hint": refresh_token,
        }
        newurl = self.__oauth2_config.login_out_url
        # 使用urlencode将字典转换为URL编码的字符串
        query_string = urlencode(token_parameters)

        # 拼接完整的URL
        newurl = newurl + "?" + query_string

        resp_json: dict = await http_request.get_json(
            newurl, headers={"Content-Type": "application/x-www-form-urlencoded"}
        )
        # print('调用 ',newurl,token_parameters,resp_json)
        return ""


oauth2_client = OAuth2Client()
