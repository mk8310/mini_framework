from abc import ABC, abstractmethod
from typing import Any, Dict, List, Type

from mini_framework.web.std_models.base_model import BaseViewModel


class DataTask(ABC):
    """
    任务基类，定义了任务的基本属性和方法。
    """
    def __init__(self):
        self.__name = ""
        self.__data = None
        self.__result = None

    @property
    def name(self):
        """
        任务名称
        :return:
        """
        return self.__name

    @name.setter
    def name(self, value):
        """
        设置任务名称
        :param value: 任务名称
        :return:
        """
        self.__name = value

    def set_data(self, value):
        """
        设置任务的输入数据
        :param value: 输入数据
        :return:
        """
        self.__data = value

    @property
    def _data(self):
        """
        获取任务的输入数据
        :return:
        """
        return self.__data

    @property
    def result(self):
        """
        获取任务的处理结果
        :return: 处理结果
        """
        return self.__result

    def execute(self) -> Any:
        """
        执行具体的任务逻辑，可以处理或传递数据。
        :return: 处理后的数据，可以是任何类型。
        """
        self.__result = self._execute()
        return self.__result

    @abstractmethod
    def _execute(self) -> Any:
        """
        执行具体的任务逻辑，可以处理或传递数据。
        :return: 处理后的数据，可以是任何类型。
        """
        pass


class DataReader(DataTask):

    @abstractmethod
    def register_model(self, model_key: str, model: Type[BaseViewModel]):
        """
        设置数据读取模型
        :param model_key: 模型编码
        :param model: 数据的Pydantic模型
        :return:
        """
        pass

    @abstractmethod
    def _execute(self) -> Dict[str, List[BaseViewModel]]:
        pass


class DataWriter(DataTask):

    @abstractmethod
    def add_data(self, entity_key: str, data: List[BaseViewModel]):
        """
        添加待处理的数据，需要符合pydantic规范
        :param entity_key: 数据编码
        :param data: 模型数据清单
        :return:
        """
        pass

    @abstractmethod
    def _execute(self):
        pass
