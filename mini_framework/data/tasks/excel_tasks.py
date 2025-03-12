from typing import Dict, Type, List

import pandas as pd

from mini_framework.data.tasks.datatask import DataReader, DataWriter
from mini_framework.web.std_models.base_model import BaseViewModel


class ExcelReader(DataReader):
    """
    从Excel文件中读取数据并将其转换为Pydantic模型的实例
    """

    def __init__(self):
        # 初始化模型与sheet名称的映射字典
        self.model_sheet_map: Dict[Type[BaseViewModel], tuple[str, any]] = {}
        super().__init__()
        self.name = "excel_reader"

    def register_model(self, sheet_name: str, model: Type[BaseViewModel], header=0):
        """
        注册模型和对应的Excel sheet名称
        :param sheet_name: Excel sheet名称
        :param model: Pydantic模型
        :param header: 表头行数，默认为0，表示第一行是表头
        """
        if model in self.model_sheet_map:
            raise ValueError(
                f"Model {model.__name__} is already registered with a sheet."
            )
        kwargs = dict(header=header)
        self.model_sheet_map[model] = (sheet_name, kwargs)

    def _execute(self) -> Dict[str, List[BaseViewModel]]:
        """
        读取Excel文件并将数据转换为pydantic模型的实例
        """
        if not self.model_sheet_map:
            raise ValueError("No models registered.")
        result = {}
        xls = pd.ExcelFile(self._data)

        for model_cls, (sheet_name, kwargs) in self.model_sheet_map.items():
            if sheet_name not in xls.sheet_names:
                raise ValueError(f"Sheet '{sheet_name}' not found in the Excel file.")

            df = pd.read_excel(xls, sheet_name=sheet_name, **kwargs)
            model_titles = {
                f.title: name for name, f in model_cls.model_fields.items() if f.title
            }
            columns_mapping = {
                title: col for title, col in model_titles.items() if title in df.columns
            }

            model_instances = [
                model_cls(**row)
                for index, row in df[columns_mapping.keys()]
                .rename(columns=columns_mapping)
                .iterrows()
            ]
            result[sheet_name] = model_instances

        return result


class ExcelWriter(DataWriter):
    """
    将Pydantic模型的实例转换为Excel文件
    """

    def __init__(self):
        """
        初始化ExcelWriter类
        """

        super().__init__()
        self.__excel_data: Dict[str, List[BaseViewModel]] = {}
        self.name = "excel_writer"

    def add_data(self, sheet_name: str, data: List[BaseViewModel]):
        """
        添加数据到Excel文件
        :param sheet_name: 工作表名称
        :param data: 数据列表
        """
        self.__excel_data[sheet_name] = data

    def _execute(self):
        """
        将pydantic模型的实例转换为Excel文件，使用字段的title作为列标题
        """

        with pd.ExcelWriter(self._data, engine="xlsxwriter") as xls:
            for sheet_name, data in self.__excel_data.items():
                if not data:  # 检查数据列表是否非空
                    continue
                # 首先，使用pydantic的schema()方法获取字段定义
                schema = data[0].model_json_schema()
                properties = schema.get("properties", {})
                column_titles = {
                    key: properties[key].get("title", key) for key in properties
                }

                # 使用pydantic的json()方法将每个模型转换成字典，然后创建DataFrame
                df = pd.DataFrame([item.model_dump() for item in data])

                # 替换DataFrame的列名为用户定义的title
                df.rename(columns=column_titles, inplace=True)

                # 写入Excel文件中的对应工作表
                df.to_excel(xls, sheet_name=sheet_name, index=False)
        return self._data
