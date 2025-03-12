import re

from .transformer import Transformer


class Replace(Transformer):
    """Replace Transform 配置类"""

    def __init__(self, source_table_name, result_table_name, replace_field, pattern, is_regex, replacement):
        """
        初始化 Replace Transform 配置
        :param source_table_name: 源表名
        :param result_table_name: 结果表名
        :param replace_field: 需要替换的字段
        :param pattern: 匹配的正则表达式
        :param is_regex: 是否是正则表达式
        :param replacement: 替换的内容
        """
        super().__init__(plugin="Replace")
        self._replace_field = replace_field
        self._pattern = pattern
        self._is_regex = is_regex
        self._replacement = replacement
        self._source_table_name = source_table_name
        self._result_table_name = result_table_name

    def to_plugin_dict(self):
        return {
            "source_table_name": self.source_table_name,
            "result_table_name": self.result_table_name,
            "replace_field": self._replace_field,
            "pattern": self._pattern,
            "is_regex": self._is_regex,
            "replacement": self._replacement,
        }

    def validate(self):
        if not self._replace_field:
            raise ValueError("replace_field 不能为空")
        if not self._replacement:
            raise ValueError("replacement 不能为空")
        if not self._pattern:
            raise ValueError("pattern 不能为空")
        if self._is_regex is None:
            raise ValueError("is_regex 不能为空")
        # 当 is_regex 为 True 时，pattern 不能为空且必须是合法的正则表达式
        if self._is_regex and not re.compile(self._pattern):
            raise ValueError("pattern 不是合法的正则表达式")
        super().validate()
