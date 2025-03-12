import urllib
from json.decoder import JSONDecodeError

import httpx

from mini_framework.design_patterns.singleton import singleton
from mini_framework.utils.json import JsonUtils
from mini_framework.web.std_models.errors import MiniHTTPException


def _raise_response_error(response: httpx.Response):
    """
    抛出响应错误
    :param response:
    :return:
    """
    if response.status_code >= 400:
        try:
            resp_content = response.json()
        except (JSONDecodeError, TypeError):
            resp_content = response.text
        status_code = 400
        if response.status_code > 500:
            status_code = response.status_code
        raise MiniHTTPException(
            status_code=status_code,
            error_code="API_CALL_ERROR",
            details=resp_content,
            detail="API 请求失败",
            user_message="API 请求失败",
            stack=None,
            headers=None
        )


def join_url_path(*paths):
    """
    拼接 URL 路径
    :param paths:
    :return:
    """
    return "/".join([str(path).strip("/") for path in paths])


@singleton
class HTTPRequest(object):
    __connected = False
    __client = None

    def __response_json(self, response):
        """

        :param response:
        :return:
        """
        result = response.text
        return JsonUtils.json_str_to_dict(result)

    def startup(self):
        max_connections: int = 100
        max_keepalive: int = 20
        timeout: float = 10.0
        limits = httpx.Limits(
            max_connections=max_connections,
            max_keepalive_connections=max_keepalive
        )
        self.__client = httpx.AsyncClient(limits=limits, timeout=timeout)

    async def shutdown(self):
        if self.__client:
            await self.__client.aclose()

    @property
    def client(self):
        return self.__client

    async def post_json(self, url: str, data: dict = None, headers: dict = None):
        """
        发送 POST 请求, 返回 JSON 数据
        :param url:
        :param data:
        :param headers:
        :return:
        """
        # 
        # 发送 POST 请求
        response = await self.__client.post(url, json=data, headers=headers)
        # 返回响应数据
        _raise_response_error(response)
        return self.__response_json(response)

    async def post(self, url: str, data: dict = None, headers: dict = None):
        """
        发送 POST 请求
        :param url:
        :param data:
        :param headers:
        :return:
        """
        # 
        response = await self.__client.post(url, data=data, headers=headers)
        # 返回响应数据
        _raise_response_error(response)
        return response.text

    async def get_json(self, url: str, headers: dict = None):
        """
        发送 GET 请求
        :param url:
        :param headers:
        :return:
        """
        # 
            # 发送 GET 请求
        response = await self.__client.get(url, headers=headers)
        # 返回响应数据
        _raise_response_error(response)
        return self.__response_json(response)

    async def get(self, url: str, headers: dict = None):
        """
        发送 GET 请求
        :param url:
        :param headers:
        :return:
        """
        # 
        # 发送 GET 请求
        response = await self.__client.get(url, headers=headers)
        # 返回响应数据
        _raise_response_error(response)
        return response.text

    async def put_json(self, url: str, data: dict = None, headers: dict = None):
        """
        发送 PUT 请求
        :param url:
        :param data:
        :param headers:
        :return:
        """
        
        # 发送 PUT 请求
        response = await self.__client.put(url, json=data, headers=headers)
        # 返回响应数据
        _raise_response_error(response)
        return self.__response_json(response)

    async def put(self, url: str, data: dict = None, headers: dict = None):
        """
        发送 PUT 请求
        :param url:
        :param data:
        :param headers:
        :return:
        """
        
        # 发送 PUT 请求
        response = await self.__client.put(url, data=data, headers=headers)
        # 返回响应数据
        _raise_response_error(response)
        return response.text

    async def delete_json(self, url: str, headers: dict = None):
        """
        发送 DELETE 请求
        :param url:
        :param headers:
        :return:
        """
        
        # 发送 DELETE 请求
        response = await self.__client.delete(url, headers=headers)
        # 返回响应数据
        _raise_response_error(response)
        return self.__response_json(response)

    async def delete(self, url: str, headers: dict = None):
        """
        发送 DELETE 请求
        :param url:
        :param headers:
        :return:
        """
        
        # 发送 DELETE 请求
        response = await self.__client.delete(url, headers=headers)
        # 返回响应数据
        _raise_response_error(response)
        return response.text

    async def patch_json(self, url: str, data: dict = None, headers: dict = None):
        """
        发送 PATCH 请求
        :param url:
        :param data:
        :param headers:
        :return:
        """
        
        # 发送 PATCH 请求
        response = await self.__client.patch(url, json=data, headers=headers)
        # 返回响应数据
        _raise_response_error(response)
        return self.__response_json(response)

    async def patch(self, url: str, data: dict = None, headers: dict = None):
        """
        发送 PATCH 请求
        :param url:
        :param data:
        :param headers:
        :return:
        """
        
        # 发送 PATCH 请求
        response = await self.__client.patch(url, data=data, headers=headers)
        # 返回响应数据
        _raise_response_error(response)
        return response.text

    def build_url(self, base_url, params):
        """
        将字典对象转换为URL查询参数并附加到给定的基本URL

        :param base_url: str, 基本URL，例如 "http://www.aaa.com/"
        :param params: dict, 查询参数字典，例如 {"a": 1, "b": 2}
        :return: str, 生成的完整URL
        """
        query_string = urllib.parse.urlencode(params)
        return f"{base_url}?{query_string}"


http_request = HTTPRequest()
