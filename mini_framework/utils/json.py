from __future__ import annotations

import hashlib
import json
from datetime import datetime, date
from typing import Any

from mini_framework.utils.json_deserialize import DefaultJSONDecoder
from mini_framework.utils.time import TimeUtils, DateUtil


class JsonUtils:
    @staticmethod
    def dict_to_json_str(obj: Any,separators:tuple[str,str]|None=None,ensure_ascii:bool|None=None) -> str:
        """
        将字典对象转换为json字符串
        :param obj: 字典对象
        :param separators: 分隔符
        :param ensure_ascii: 是否转换为ascii
        :return: json字符串
        """
        if not separators and not ensure_ascii:
            return json.dumps(obj, default=JsonUtils._serialize_datetime)
        elif not separators and ensure_ascii:
            return json.dumps(obj, ensure_ascii=ensure_ascii, default=JsonUtils._serialize_datetime)
        elif separators and not ensure_ascii:
            return json.dumps(obj, separators=separators, default=JsonUtils._serialize_datetime)
        else:
            return json.dumps(obj, separators=separators, ensure_ascii=ensure_ascii, default=JsonUtils._serialize_datetime)


    @staticmethod
    def json_str_to_dict(json_str: str) -> Any:
        """
        将json字符串转换为字典对象
        :param json_str: json字符串
        :return: 字典对象
        """
        return json.loads(json_str, cls=DefaultJSONDecoder)

    @staticmethod
    def normalize_json(data):
        """
        递归地对JSON对象进行排序，返回一个有序的JSON对象
        """
        if isinstance(data, dict):
            return {k: JsonUtils.normalize_json(data[k]) for k in sorted(data)}
        elif isinstance(data, list):
            return [JsonUtils.normalize_json(item) for item in data]
        else:
            return data

    @staticmethod
    def generate_sha256_signature(json_obj):
        """
        为输入的JSON对象生成固定的SHA256签名
        """
        # 对JSON对象进行归一化
        normalized_json = JsonUtils.normalize_json(json_obj)

        # 将归一化后的JSON对象转化为字符串
        json_string = JsonUtils.dict_to_json_str(normalized_json, separators=(",", ":"), ensure_ascii=False)

        # 使用SHA256生成签名
        sha256_hash = hashlib.sha256(json_string.encode("utf-8")).hexdigest()

        return sha256_hash

    @staticmethod
    def _serialize_datetime(obj: Any) -> Any:
        """
        序列化datetime对象
        :param obj:
        :return:
        """
        if isinstance(obj, datetime):
            return TimeUtils.format(obj)
        elif isinstance(obj, date):
            return DateUtil.format(obj)
        return obj
