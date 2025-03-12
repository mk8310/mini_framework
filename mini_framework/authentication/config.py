from pydantic import Field

from mini_framework.design_patterns.singleton import singleton
from mini_framework.web.std_models.base_model import BaseViewModel


class JWTConfig(BaseViewModel):
    secret: str = Field(..., title="JWT Secret", description="JWT Secret Key")
    algorithm: str = Field("HS256", title="JWT Algorithm", description="JWT 加密算法")
    expires: int = Field(..., title="JWT Expires", description="JWT 过期时间")
    issuer: str = Field(..., title="JWT Issuer", description="JWT 签发者")
    issue_at: int = Field(..., title="JWT Issue At", description="JWT 签发时间")
    # audience: str = Field( "", title="", description="")


class OAuth2Config(BaseViewModel):
    """
    OAuth2 配置
    """

    client_id: str = Field(..., title="Client ID", description="OAuth2 Client ID")
    client_secret: str = Field(
        ..., title="Client Secret", description="OAuth2 Client Secret"
    )
    # endpoint: str = Field("", title="Endpoint", description="OAuth2 Endpoint")
    redirect_url: str = Field("", title="Redirect URL", description="OAuth2 重定向地址")
    scope: str = Field(..., title="Scope", description="OAuth2 Scope")
    cert: str = Field("", title="Cert", description="OAuth2 证书内容")
    organization: str = Field("", title="Organization", description="OAuth2 组织编号")
    application: str = Field("", title="Application", description="OAuth2 应用编号")
    home_url: str = Field(..., title="Home URL", description="当前应用首页地址")
    no_login_urls: list[str] = Field(
        [], title="No login urls", description="不需要登录的URL前缀"
    )
    authorization_url: str = Field(
        "", title="Authorization URL", description="OAuth2 授权地址"
    )
    token_url: str = Field("", title="Token URL", description="OAuth2 访问令牌地址")
    grant_type: str = Field(
        "authorization_code", title="Grant Type", description="OAuth2 授权类型"
    )
    user_info_url: str = Field(
        "", title="User Info URL", description="OAuth2 用户信息地址"
    )
    login_out_url: str = Field("", title="Login Out URL", description="OAuth2 登出地址")


@singleton
class AuthenticationConfig:
    def __init__(self):
        from mini_framework.configurations import config_injection

        manager = config_injection.get_config_manager()
        auth_dict = manager.get_domain_config("authentication")
        if not auth_dict:
            raise ValueError("authentication config not found")
        self.oauth2 = OAuth2Config(**auth_dict["oauth2"])
        self.jwt = JWTConfig(**auth_dict["jwt"])


authentication_config = AuthenticationConfig()

"""
{
    "authentication":{
        "jwt":{
            "secret": "secret",
            "algorithm": "HS256",
            "expires": 3600,
            "issuer": "issuer",
            "audience": "audience",
            "issue_at": 0
        },
        "oauth2":{
            "client_id": "client_id",
            "client_secret": "client_secret",
            "authorization_url": "authorization_url",
            "token_url": "token_url",
            "redirect_url": "redirect_url",
            "scope": "scope",
            "home_url": "home_url"
        }
    }
}
"""
