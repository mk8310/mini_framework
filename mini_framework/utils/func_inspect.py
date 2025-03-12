import inspect
import re
from types import UnionType, GenericAlias
from typing import Optional, Dict, get_origin

from mini_framework.utils.log import logger
from mini_framework.web.std_models.base_model import BaseViewModel


class MethodSummary:
    def __init__(self, summary: str):
        summary_lines = summary.split("\n", 1)
        self.__title = summary_lines[0]
        self.__description = summary_lines[1] if len(summary_lines) > 1 else ""

    @property
    def title(self) -> str:
        return self.__title

    @property
    def description(self) -> str:
        return self.__description


class ParameterDoc:
    def __init__(self, name: str, description: str):
        self.__name = name
        self.__description = description

    @property
    def name(self) -> str:
        return self.__name

    @property
    def description(self) -> str:
        return self.__description


class ReturnDoc:
    def __init__(self, description: str):
        self.__description = description

    @property
    def description(self) -> str:
        return self.__description


class Function:
    def __init__(self, func: callable):
        if not callable(func):
            raise ValueError("func must be a callable object (function, method, etc.)")
        self.__func = func
        self.__summary = None
        self.__params_docs = dict()
        self.__parameters = None
        self.__return_doc = None
        self.__return_annotation = None
        self.__method_name = None
        self.__method_path = None
        self.__func_signature = None
        self.__inspect_function()

    @property
    def summary(self) -> MethodSummary:
        return self.__summary

    @property
    def params_docs(self) -> Dict[str, ParameterDoc]:
        return self.__params_docs

    @property
    def return_doc(self) -> Optional[ReturnDoc]:
        return self.__return_doc

    @property
    def method_name(self) -> str:
        return self.__method_name

    @property
    def method_path(self) -> str:
        return self.__method_path

    @property
    def return_annotation(self):
        return self.__return_annotation

    @property
    def signature(self):
        return self.__func_signature

    @property
    def parameters(self):
        return self.__parameters

    @property
    def parameters_without_self(self):
        return {k: v for k, v in self.__parameters.items() if k != "self"}

    def return_annotation_can_serialize(self):
        """
        验证返回类型注解是否为可序列化的类型
        :return: 是否为可序列化的类型
        """
        serializable_types = (
            int,
            float,
            str,
            list,
            tuple,
            bool,
            dict,
            BaseViewModel,
        )

        # 如果没有定义返回类型注解，则返回 False
        if self.__return_annotation is inspect.Signature.empty:
            return False

        # 检查返回类型是否为可序列化的类型
        if (
                (isinstance(self.__return_annotation, type) and issubclass(self.__return_annotation, serializable_types))
                or
                (isinstance(self.__return_annotation, (GenericAlias, UnionType)) and any((t for t in self.__return_annotation.__args__ if issubclass(t, serializable_types))))
                or
                (get_origin(self.__return_annotation) and any((t for t in self.__return_annotation.__args__ if issubclass(t, serializable_types))))  # typing.List[int]

        ):
            return True
        return False

    def __inspect_function(self):
        """
        解析函数的文档字符串
        :return:
        """
        try:
            # 获取函数的注释和签名
            docstring = inspect.getdoc(self.__func)
            self.__func_signature = inspect.signature(self.__func)
        except (TypeError, ValueError) as e:
            raise ValueError(f"Error inspecting function: {e}")

        # 初始化变量
        summary = None
        params = {}
        return_doc = None
        self.__method_name = self.__func.__name__
        self.__method_path = self.__func.__qualname__
        self.__return_annotation = self.__func_signature.return_annotation
        self.__parameters = self.__func_signature.parameters

        if docstring:
            # 使用正则表达式分割summary、参数、返回值部分
            try:
                # summary_match = re.search(r'^(.*?)(?:\n\n|$)', docstring, re.S)
                summary_match = re.search(r'^(.*?)(?=\n:param|\n:returns?:|$)', docstring, re.S)
                if summary_match:
                    summary = MethodSummary(summary_match.group(1).strip())
            except re.error as e:
                logger.info(f"Error parsing summary with regex: {e}")

            try:
                params_match = re.findall(r'^:param (\w+): (.*?)$', docstring, re.M)
                for param_name, param_desc in params_match:
                    params[param_name] = ParameterDoc(name=param_name, description=param_desc.strip())
            except re.error as e:
                logger.info(f"Error parsing parameters with regex: {e}")
            except Exception as e:
                logger.info(f"Error processing parameter documentation: {e}")

            try:
                return_match = re.search(r'^:returns?: (.*?)$', docstring, re.M)
                if return_match:
                    return_doc = ReturnDoc(description=return_match.group(1).strip())
            except re.error as e:
                logger.info(f"Error parsing return annotation with regex: {e}")
            except Exception as e:
                logger.info(f"Error processing return annotation: {e}")

        self.__summary = summary
        self.__params_docs = params
        self.__return_doc = return_doc
