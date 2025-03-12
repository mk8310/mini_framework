import json
from datetime import datetime, date

from mini_framework.utils.time import DateUtil, TimeUtils

import re


def validate_date_format(target_str, format_str):
    # 定义日期时间转义符及其对应的正则表达式
    format_dict = {
        '%Y': r'\d{4}',
        '%y': r'\d{2}',
        '%m': r'\d{2}',
        '%d': r'\d{2}',
        '%H': r'\d{2}',
        '%I': r'\d{2}',
        '%M': r'\d{2}',
        '%S': r'\d{2}',
        '%f': r'\d{6}',
        '%a': r'\w+',
        '%A': r'\w+',
        '%b': r'\w+',
        '%B': r'\w+',
        '%c': r'.+',
        '%j': r'\d{3}',
        '%p': r'(AM|PM)',
        '%U': r'\d{2}',
        '%w': r'[0-6]',
        '%W': r'\d{2}',
        '%x': r'.+',
        '%X': r'.+',
        '%Z': r'\w+',
        '%%': r'%'
    }

    # 替换格式字符串中的转义符为对应的正则表达式
    regex_str = format_str
    for key, value in format_dict.items():
        regex_str = regex_str.replace(key, value)

    # 使用生成的正则表达式来验证目标字符串
    pattern = re.compile(regex_str)
    match = pattern.fullmatch(target_str)
    return match is not None


class DateParser:
    """日期解析策略的基类"""

    def __init__(self, format_str: str):
        self.__format_str = format_str

    @property
    def format_str(self):
        return self.__format_str

    def parse(self, date_str):
        if not validate_date_format(date_str, self.__format_str):
            return None
        return self._parse(date_str)

    def _parse(self, date_str):
        raise NotImplementedError


class ISODateParser(DateParser):
    """解析ISO 8601日期格式"""
    def __init__(self):
        super().__init__('%Y-%m-%dT%H:%M:%S')

    def _parse(self, date_str):
        try:
            return TimeUtils.from_iso_format(date_str)
        except ValueError:
            return None


class DefaultFormatDatetimeParser(DateParser):
    """解析自定义日期格式，例如 'YYYY-MM-DD HH:MM:SS'"""

    def _parse(self, date_str):
        try:
            return TimeUtils.parse(date_str, self.format_str)
        except ValueError:
            return None


class DefaultFormatDateParser(DateParser):
    def _parse(self, date_str):
        # 验证日期格式是否符合date_format的格式

        try:
            return DateUtil.parse(date_str, self.format_str)
        except ValueError:
            return None


class DateParserContext:
    """策略模式的上下文环境，用于执行日期解析"""

    def __init__(self, *parsers):
        self.parsers = parsers

    def parse_date(self, date_str):
        for parser in self.parsers:
            result = parser.parse(date_str)
            if result:
                return result
        return date_str  # 如果所有解析器都失败了，返回原始字符串


class DefaultJSONDecoder(json.JSONDecoder):
    def __init__(self, *args, **kwargs):
        self.date_parser_context = DateParserContext(
            ISODateParser(),
            DefaultFormatDateParser('%Y-%m-%d'),
            DefaultFormatDatetimeParser('%Y-%m-%d %H:%M:%S')
        )
        super().__init__(object_hook=self._object_hook, *args, **kwargs)

    def _object_hook(self, obj):
        for key, value in obj.items():
            if isinstance(value, str):
                # 尝试解析日期时间
                obj[key] = self.date_parser_context.parse_date(value)
        return obj

class DefaultJSONEncoder(json.JSONEncoder):
    """
    JSONEncoder 子类，用于处理 datetime 和 date 类型的数据
    datetime 格式: %Y-%m-%d %H:%M:%S.%f
    date 格式: %Y-%m-%d
    """

    def default(self, o):
        if isinstance(o, (datetime, date)):
            return o.strftime('%Y-%m-%d %H:%M:%S.%f') if \
                isinstance(o, datetime) else \
                o.strftime('%Y-%m-%d')
        return super().default(o)