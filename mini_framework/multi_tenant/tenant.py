import time
from enum import Enum

from pydantic import Field

from mini_framework.web.std_models.base_model import BaseViewModel

EXP_SECONDS = 60 * 60 * 24 * 30


class TenantStatus(str, Enum):
    active = "active"
    inactive = "inactive"
    expired = "expired"


class Tenant(BaseViewModel):
    code: str = Field(..., title="租户编码", description="租户编码")
    name: str = Field(..., title="租户名称", description="租户名称")
    description: str = Field("", title="租户描述", description="租户描述")
    cache_time: int = Field(0, title="缓存时间", description="缓存产生的时间")
    status: TenantStatus = Field(
        TenantStatus.active, title="租户状态", description="租户状态"
    )
    client_id: str = Field(..., title="Client ID", description="OAuth2 Client ID")
    client_secret: str = Field(
        ..., title="Client Secret", description="OAuth2 Client Secret"
    )
    redirect_url_template: str|None = Field(
        None, title="Redirect URL", description="OAuth2 重定向地址"
    )
    home_url: str|None = Field(None, title="Home URL", description="OAuth2 主页地址")
    redirect_url_args: dict = Field(
        None, title="Redirect URL Args", description="重定向地址参数"
    )
    cert_content: str = Field(None, title="Cert Content", description="证书内容")

    @property
    def redirect_url(self) -> str:
        """
        根据 redirect_url_template 获取重定向地址
        :return: 重定向地址
        """
        redirect_url_args = self.redirect_url_args.copy() if self.redirect_url_args else {}
        if "tenant" not in redirect_url_args:
            redirect_url_args["tenant"] = self.code
        redirect_url_template = self.redirect_url_template
        if not self.redirect_url_template:
            from mini_framework.authentication.config import authentication_config

            redirect_url_template = authentication_config.oauth2.redirect_url
        if not redirect_url_args:
            return redirect_url_template
        # 判断self.redirect_url_template中是否有可待替换的参数
        if "{" in redirect_url_template:
            # 验证self.redirect_url_template中的参数是否都在self.redirect_url_args中
            not_exists_keys = []
            for key in redirect_url_args:
                if "{" + key + "}" not in redirect_url_template:
                    not_exists_keys.append(key)
            if len(not_exists_keys) > 0:
                not_exists_keys_str = ", ".join(not_exists_keys)
                raise ValueError(
                    f"redirect_url_args key {not_exists_keys_str} not in redirect_url_template"
                )
            return redirect_url_template.format(**redirect_url_args)
        return redirect_url_template

    @property
    def cache_expired(self):
        """
        判断租户是否过期，根据缓存时间判断
        :return:
        """
        if self.cache_time is None:
            return True
        if self.status == TenantStatus.expired:
            return True
        return self.cache_time + EXP_SECONDS > int(time.time())
