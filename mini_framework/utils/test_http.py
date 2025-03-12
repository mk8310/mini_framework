import json
import urllib
from json.decoder import JSONDecodeError

import httpx


def join_url_path(*paths):
    """
    拼接 URL 路径
    :param paths:
    :return:
    """
    return "/".join([str(path).strip("/") for path in paths])

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
        raise ValueError()

class HTTPRequest(object):

    def __response_json(self, response):
        """

        :param response:
        :return:
        """
        result = response.text
        return json.loads(result)

    async def post_json(self, url: str, data: dict = None, headers: dict = None):
        """
        发送 POST 请求, 返回 JSON 数据
        :param url:
        :param data:
        :param headers:
        :return:
        """
        async with httpx.AsyncClient() as client:
            # 发送 POST 请求
            response = await client.post(url, json=data, headers=headers)
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
        async with httpx.AsyncClient() as client:
            # 发送 POST 请求
            response = await client.post(url, data=data, headers=headers)
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
        async with httpx.AsyncClient() as client:
            # 发送 GET 请求
            response = await client.get(url, headers=headers)
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
        async with httpx.AsyncClient() as client:
            # 发送 GET 请求
            response = await client.get(url, headers=headers)
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
        async with httpx.AsyncClient() as client:
            # 发送 PUT 请求
            response = await client.put(url, json=data, headers=headers)
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
        async with httpx.AsyncClient() as client:
            # 发送 PUT 请求
            response = await client.put(url, data=data, headers=headers)
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
        async with httpx.AsyncClient() as client:
            # 发送 DELETE 请求
            response = await client.delete(url, headers=headers)
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
        async with httpx.AsyncClient() as client:
            # 发送 DELETE 请求
            response = await client.delete(url, headers=headers)
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
        async with httpx.AsyncClient() as client:
            # 发送 PATCH 请求
            response = await client.patch(url, json=data, headers=headers)
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
        async with httpx.AsyncClient() as client:
            # 发送 PATCH 请求
            response = await client.patch(url, data=data, headers=headers)
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
