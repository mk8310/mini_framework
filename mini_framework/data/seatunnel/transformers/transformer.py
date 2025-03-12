from abc import ABC

from ..plugin import Plugin


class Transformer(Plugin, ABC):
    """Seatunnel transform 配置类"""

    def __init__(self, plugin: str):
        self._source_table_name = ""
        self._result_table_name = ""
        super().__init__(plugin=plugin)

    @property
    def source_table_name(self):
        return self._source_table_name

    @property
    def result_table_name(self):
        return self._result_table_name

    def validate(self):
        if not self._source_table_name:
            raise ValueError("source_table_name 不能为空")
        if not self._result_table_name:
            raise ValueError("result_table_name 不能为空")
        super().validate()

    def to_dict(self):
        return {
            "source_table_name": self._source_table_name,
            "result_table_name": self._result_table_name,
            **self._to_dict(),
        }
