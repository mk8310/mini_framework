import os

from fastapi.openapi.docs import get_swagger_ui_html, get_redoc_html
from fastapi.openapi.utils import get_openapi
from starlette.staticfiles import StaticFiles

from ..authentication.config import authentication_config
from ..web.mini_app import Application, app_config


def get_openapi_url():
    return f"/api/{app_config.name}/openapi.json"


def get_docs_url():
    return f"/api/{app_config.name}/docs"


def get_redoc_url():
    return f"/api/{app_config.name}/re/docs"


async def docs():
    return get_swagger_ui_html(
        openapi_url=get_openapi_url(),
        title=app_config.name + " - API Document",
        oauth2_redirect_url=authentication_config.oauth2.redirect_url,
        swagger_js_url=f"/api/{app_config.name}/api-docs-assets/swagger-ui/swagger-ui-bundle.js",
        swagger_css_url=f"/api/{app_config.name}/api-docs-assets/swagger-ui/swagger-ui.css",
    )


async def redoc():
    return get_redoc_html(
        openapi_url=get_openapi_url(),
        title=app_config.name + " - API Document",
        with_google_fonts=False,
        redoc_js_url=f"/api/{app_config.name}/api-docs-assets/redoc-ui/redoc.standalone.js",
    )


class APIDocumentManager(object):

    @property
    def config(self):
        return dict(docs_url=get_docs_url(), redoc_url=get_redoc_url())

    def register(self, application: Application):
        current_dir_path = os.path.dirname(os.path.abspath(__file__))
        api_static_path = f"{current_dir_path}/resources/statics"
        application.mount(
            f"/api/{app_config.name}/api-docs-assets",
            StaticFiles(directory=api_static_path),
            name="api-docs-assets",
        )
        openapi_schema = application.openapi_schema
        if not application.openapi_schema:
            # return application.openapi_schema
            openapi_schema = get_openapi(
                title=app_config.title,
                version=app_config.version,
                description=app_config.description,
                routes=application.routes,
            )
        # 确保components对象存在，并初始化securitySchemes
        schema_components = openapi_schema["components"]
        if "components" not in openapi_schema:
            schema_components = {}
        if "securitySchemes" not in schema_components:
            schema_components["securitySchemes"] = {}
        #
        # 定义JWT授权类型
        schema_components["securitySchemes"]["BearerAuth"] = {
            "type": "http",
            "scheme": "bearer",
            "bearerFormat": "JWT",
        }
        schema_components["securitySchemes"]["OAuth2"] = {
            "type": "oauth2",
            "flows": {
                "authorizationCode": {
                    "authorizationUrl": authentication_config.oauth2.authorization_url,
                    "tokenUrl": authentication_config.oauth2.token_url,
                    "redirectUri": authentication_config.oauth2.redirect_url
                }
            },
        }
        schema_components["securitySchemes"]["Tenant"] = {
            "type": "apiKey",
            "in": "header",
            "name": "X-TENANT-CODE",
        }
        openapi_schema["info"]["title"] = app_config.title
        openapi_schema["info"]["version"] = app_config.version
        openapi_schema["info"]["description"] = app_config.description

        # 添加全局授权规则，使得所有接口默认需要JWT验证，也可以对特定接口设置
        openapi_schema["security"] = [
            {"BearerAuth": []},
            {"OAuth2": ["read:users", "write:users"]},
            {"Tenant": []},
        ]
        application.openapi_schema = openapi_schema
