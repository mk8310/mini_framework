from ..plugin import Plugin


class DataSink:
    def __init__(self, plugin: Plugin, source_table_name, parallelism=None):
        """
        初始化 Seatunnel Sink 配置
        :param source_table_name: 当不指定 source_table_name 时，当前插件处理配置文件中上一个插件输出的数据集 dataset; 当指定了 source_table_name 时，当前插件正在处理该参数对应的数据集
        :param parallelism: 当没有指定parallelism时，默认使用 env 中的 parallelism。当指定 parallelism 时，它将覆盖 env 中的 parallelism。
        """

        self._source_table_name = source_table_name
        self._parallelism = parallelism
        self._plugin = plugin

    @property
    def source_table_name(self):
        return self._source_table_name

    @property
    def parallelism(self):
        return self._parallelism

    @property
    def plugin(self):
        return self._plugin

    def to_dict(self):
        result = self._plugin.to_plugin_dict()
        if self._parallelism is not None:
            result["parallelism"] = self._parallelism
        if self._source_table_name is not None:
            result["source_table_name"] = self._source_table_name
        return result

    def validate(self):
        if self._source_table_name is None:
            raise ValueError("source_table_name 不能为空")
        self._plugin.validate()
