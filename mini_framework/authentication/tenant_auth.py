from .config import authentication_config
from ..multi_tenant.tenant import Tenant


class TenantAuthorizationInfo:
    def __init__(self, tenant: Tenant):
        self.__tenant: Tenant = tenant
        self.__oauth2_config = authentication_config.oauth2

    @property
    def home_url(self):
        if not self.__tenant:
            return self.__oauth2_config.home_url
        tenant_code = self.__tenant.code
        if "{tenant}" in self.__oauth2_config.home_url:
            glb_home_url = self.__oauth2_config.home_url.format(tenant=tenant_code)
        else:
            glb_home_url = self.__oauth2_config.home_url
        return (
            glb_home_url
            if self.__tenant is None or not self.__tenant.home_url
            else self.__tenant.home_url
        )

    def get_redirect_url(self, refer_uri: str = "") -> str:
        from urllib.parse import urlencode

        tenant_code = self.__tenant.code if self.__tenant else ""
        if "{tenant}" in self.__oauth2_config.redirect_url:
            glb_redirect_url = self.__oauth2_config.redirect_url.format(
                tenant=tenant_code
            )
        else:
            glb_redirect_url = self.__oauth2_config.redirect_url
        redirect_url = (
            glb_redirect_url
            if self.__tenant is None or not self.__tenant.redirect_url
            else self.__tenant.redirect_url
        )

        params = dict()
        if "?" in redirect_url:
            # 获取url中的参数并构建参数dict
            params = dict(
                [param.split("=") for param in redirect_url.split("?")[1].split("&")]
            )
        if tenant_code:
            params["tenant_code"] = tenant_code
        if refer_uri:
            params["refer_uri"] = refer_uri
        # 重新构建url
        redirect_url = redirect_url.split("?")[0]
        url_params = urlencode(params)
        if len(url_params) > 0:
            return f"{redirect_url}?{url_params}"
        return redirect_url

    @property
    def client_id(self):
        return (
            self.__oauth2_config.client_id
            if self.__tenant is None
            else self.__tenant.client_id
        )

    @property
    def client_secret(self):
        return (
            self.__oauth2_config.client_secret
            if self.__tenant is None
            else self.__tenant.client_secret
        )

    @property
    def authorization_url(self):
        return self.__oauth2_config.authorization_url

    @property
    def token_url(self):
        return self.__oauth2_config.token_url

    @property
    def user_info_url(self):
        return self.__oauth2_config.user_info_url
