from ..plugin import Plugin


class DataSource:
    def __init__(self, plugin: Plugin, result_table_name, parallelism=None, **kwargs):
        """
        初始化 Seatunnel DataSource 配置。
        在作业配置中使用 result_table_name 时，必须设置 source_table_name 参数。
        :param plugin: 插件配置
        :param result_table_name: 当未指定 result_table_name 时，此插件处理的数据将不会被注册为可由其他插件直接访问的数据集 (dataStream/dataset)，或称为临时表 (table)。当指定了 result_table_name 时，此插件处理的数据将被注册为可由其他插件直接访问的数据集 (dataStream/dataset)，或称为临时表 (table)。此处注册的数据集 (dataStream/dataset) 可通过指定 source_table_name 直接被其他插件访问。
        :param parallelism: 当没有指定 parallelism 时，默认使用 env 中的 parallelism。当指定 parallelism 时，它将覆盖 env 中的 parallelism。
        :param kwargs:
        """

        self._result_table_name = result_table_name
        self._parallelism = parallelism
        self._plugin = plugin

    @property
    def plugin(self):
        return self._plugin

    @property
    def parallelism(self):
        return self._parallelism

    @property
    def result_table_name(self):
        return self._result_table_name

    def to_dict(self):
        result = self._plugin.to_plugin_dict()
        if self._parallelism is not None:
            result["parallelism"] = self._parallelism
        if self._result_table_name is not None:
            result["result_table_name"] = self._result_table_name
        return result

    def validate(self):
        if self._result_table_name is None:
            raise ValueError("result_table_name 不能为空")
        self._plugin.validate()