from __future__ import annotations

import jwt
from fastapi import Query, Body, Header, Path
from starlette.types import ASGIApp

from mini_framework.authentication.config import authentication_config
from mini_framework.authentication.jwt import jwt_utils
from mini_framework.authentication.oauth2 import OAuth2Client, oauth2_client
from mini_framework.context import env
from mini_framework.design_patterns.depend_inject import get_injector
from mini_framework.multi_tenant.registry import tenant_registry
from mini_framework.multi_tenant.tenant import Tenant
from mini_framework.utils.log import logger
from mini_framework.web.middlewares.base import MiddlewareBase, ResponseManager
from mini_framework.web.request_context import RequestContext, request_context_manager
from mini_framework.web.std_models.account import AccountInfo, RenderAccount
from mini_framework.web.std_models.errors import MiniHTTPException


async def _auth_code_process(code, state, tenant_code):
    """
    处理授权码
    :param code: 认证授权码
    :param state: 随机字符串
    :param tenant_code: 租户编码
    :return:
    """
    if not code:
        raise ValueError("authentication code is required")
    from mini_framework.authentication.rules.auth_rule import AuthRules

    tenant = await tenant_registry.get_tenant(tenant_code)
    tenant_oauth2_client = OAuth2Client(tenant)

    auth_rule = get_injector(AuthRules)
    access_token = await tenant_oauth2_client.get_access_token(code, state)
    account_dict = await tenant_oauth2_client.get_account_info(access_token, True)
    # 如果存在键 id不存在account_id  则赋值到account_id
    if account_dict.get("id") is not None and account_dict.get("account_id") is None:
        account_dict["account_id"] = account_dict["id"]

    print(account_dict)
    account_info = AccountInfo(**account_dict)
    await auth_rule.save_account(account_info, account_dict)
    render_account = account_info.render_account
    # 传入各个租户的配置
    print("即将开始获取 issure")

    # token = jwt_utils.issue(render_account.dict(),tenant)
    return access_token


async def auth_callback_api(
    code: str = Body(..., title="授权码", description="OAuth2 授权码"),
    state: str = Body("", title="随机状态", description="OAuth2 随机状态"),
    tenant_code: str = Header(
        None, title="租户编码", description="租户编码", alias="X-Tenant-Code"
    ),
):
    """
    OAuth2 回调 API
    :param state: 随机状态
    :param code: 授权码
    :param tenant_code: 租户编码
    :return:
    """
    token = await _auth_code_process(code, state, tenant_code)
    return dict(token=token)


async def auth_callback_debug(
    code: str = Query(..., title="授权码", description="OAuth2 授权码"),
    state: str = Query("", title="随机状态", description="OAuth2 随机状态"),
    tenant_code: str = Query(None, title="租户编码", description="租户编码"),
):
    token = await _auth_code_process(code, state, tenant_code)
    return dict(token=token)


async def auth_tenant_callback_debug(
    tenant: str = Path(..., title="租户编码", description="租户编码"),
    code: str = Query(..., title="授权码", description="OAuth2 授权码"),
    state: str = Query("", title="随机状态", description="OAuth2 随机状态"),
):
    token = await _auth_code_process(code, state, tenant)
    return dict(token=token)


async def auth_login_out():
    from mini_framework.web.mini_app import app_config

    request = request_context_manager.current()
    token = request.request.headers.get("Authorization")
    tenant = None
    auth_uri = None

    if app_config.multi_tenant:
        tenant = await get_tenant(request.request)
    if tenant:
        logger.info(f"当前租户：{tenant.code}")
    auth_uri = get_auth_url(request, tenant)

    if not token:
        auth_uri = get_auth_url(request, tenant)
        raise HTTPInvalidTokenError(auth_uri)
    token = token.split(" ")[-1]
    try:
        glb_client_id = (
            authentication_config.oauth2.client_id
            if tenant is None
            else tenant.client_id
        )
        cert = None if tenant is None else tenant.cert_content
        payload = await jwt_utils.verify(token, client_id=glb_client_id, cert=cert)
    except jwt.InvalidTokenError as ex:
        logger.exception(str(ex), exc_info=ex, stack_info=True, extra=dict(token=token))
        auth_uri = get_auth_url(request, tenant)
        raise HTTPInvalidTokenError(auth_uri)

    access_token = await oauth2_client.destroy_token(token)
    return {"home_url": auth_uri, "msg": "退出成功"}


class HTTPInvalidTokenError(MiniHTTPException):
    def __init__(self, auth_uri: str):
        super().__init__(
            status_code=401,
            error_code="AUTH_FAILED",
            detail="Invalid token",
            user_message="当前账号未登录或登录状态已过期，请重新登录",
            stack=None,
            headers={"authorize_uri": f"{auth_uri}"},
        )


def get_auth_url(request, tenant: Tenant | None):
    refer_uri = request.request.headers.get("referer", "")
    tenant_oauth2_client = OAuth2Client(tenant=tenant)
    auth_url = tenant_oauth2_client.get_authorization_url(refer_uri=refer_uri)
    return auth_url


def check_authentication(request) -> bool:
    """
    检查是否需要进行认证
    :param request:
    :return:
    """
    no_login_urls = authentication_config.oauth2.no_login_urls
    from mini_framework.web.mini_app import app_config

    no_login_urls.extend(
        [
            f"/favicon.ico",
            f"/api/{app_config.name}/openapi.json",
            f"/api/{app_config.name}/docs",
            f"/api/{app_config.name}/re/docs",
            f"/api/{app_config.name}/api-docs-assets",
        ]
    )
    routes = request.app.routes
    for no_login_url in no_login_urls:
        if no_login_url in request.url.path:
            return False

    current_route = next(
        (route for route in routes if route.path == request.url.path), None
    )

    if not current_route:
        return True

    if getattr(current_route.endpoint, "require_auth", True):
        return True

    return False


async def get_tenant(request) -> Tenant:
    """
    获取租户编码
    :param request:
    :return:
    """
    tenant_code = request.headers.get("X-Tenant-Code")
    if not tenant_code:
        tenant_code = env.get("TENANT_CODE")
    if not tenant_code:
        return None
    tenant = await tenant_registry.get_tenant(tenant_code)
    return tenant


class AuthMiddleware(MiddlewareBase):
    """
    认证中间件
    """

    def initialize(self, app: ASGIApp):
        pass

    async def before_request(self, request: RequestContext):
        from mini_framework.web.mini_app import app_config

        if not app_config.need_auth:
            return
        if not check_authentication(request.request):
            return
        token = request.request.headers.get("Authorization")
        tenant = None
        if app_config.multi_tenant:
            tenant = await get_tenant(request.request)
        if tenant:
            logger.info(f"当前租户：{tenant.code}")
        if not token:
            auth_uri = get_auth_url(request, tenant)
            raise HTTPInvalidTokenError(auth_uri)
        token = token.split(" ")[-1]
        try:
            glb_client_id = (
                authentication_config.oauth2.client_id
                if tenant is None
                else tenant.client_id
            )
            cert = None if tenant is None else tenant.cert_content
            payload = await jwt_utils.verify(token, client_id=glb_client_id, cert=cert)
        except jwt.InvalidTokenError as ex:
            logger.exception(
                str(ex), exc_info=ex, stack_info=True, extra=dict(token=token)
            )
            auth_uri = get_auth_url(request, tenant)
            raise HTTPInvalidTokenError(auth_uri)
        request.token = token
        # 如果存在键 id不存在account_id  则赋值到account_id
        if payload.get("id") is not None and payload.get("account_id") is None:
            payload["account_id"] = payload["id"]

        print(payload)

        request.current_login_account = RenderAccount(**payload)

    async def after_request(
        self, request: RequestContext, response_manager: ResponseManager
    ):
        pass
