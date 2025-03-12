import inspect
import os.path
import re
from typing import Type

from pydantic.alias_generators import to_snake

from mini_framework.context import env
from mini_framework.databases.entities import BaseDBModel
from mini_framework.databases.toolkit.generator_models.operator import DAOOperation


def _find_operation_cls_by_package(root_path, package_path: str, parent_cls: Type) -> list:
    """
    根据包路径查找所有DAOOperation的类并形成列表返回
    :param package_path: python包路径（类似a.b.c）
    :return:
    """
    import importlib
    import os
    package_path = package_path.replace(".", os.path.sep)
    os_path = os.path.join(root_path, package_path)
    if not os.path.exists(os_path):
        raise FileNotFoundError(f"package_path:{package_path.replace(os.path.sep, '.')} not found!")
    module_paths = []
    for root, dirs, files in os.walk(os_path):
        for file_name in files:
            if file_name.endswith(".py"):
                module_name = file_name[:-3]
                module_path = os.path.join(root, module_name)
                module_path = module_path.replace(root_path, "").strip(os.path.sep)
                module_path = module_path.replace(os.path.sep, ".")
                module_paths.append(module_path)
    models = []
    for module_path in module_paths:
        module_name = module_path.replace(os.path.sep, ".")
        pkgs = importlib.import_module(module_name)
        models.extend([cls for cls in pkgs.__dict__.values() if inspect.isclass(cls) and issubclass(cls, parent_cls)])
    return models


class DAOCreator:
    def __init__(self):
        self.operations = []
        root_path = os.path.dirname(os.path.abspath(__file__))
        # 获取当前包的上级目录
        root_path = os.path.dirname(root_path)
        root_path = os.path.dirname(root_path)
        root_path = os.path.dirname(root_path)

        models = _find_operation_cls_by_package(root_path, "mini_framework.databases.toolkit.generator_models",
                                                DAOOperation)
        self.auto_register_all_operations(models)

    def register_operation(self, operation):
        self.operations.append(operation)

    def generate_dao_class(self, model: Type[BaseDBModel]):
        dao_import = ("from sqlalchemy import select, func, update\n"
                      "from mini_framework.databases.entities.dao_base import DAOBase, get_update_contents\n"
                      "from mini_framework.databases.queries.pages import Paging\n"
                      "from mini_framework.web.std_models.page import PageRequest\n")
        import inspect
        module_info = inspect.getmodule(model)
        module_desc = module_info.__str__()
        module_path = re.search(r"\'(.+?)\'", module_desc).group(1)
        dao_import += f"\nfrom {module_path} import {model.__name__}\n\n"
        dao_class_header = f"{dao_import}\nclass {model.__name__}DAO(DAOBase):\n"
        dao_methods = []
        for op in self.operations:
            if issubclass(op, DAOOperation):
                code = op(model).generate_code()
                dao_methods.append(code)
        dao_methods_code = "".join(dao_methods)
        return dao_class_header + dao_methods_code

    def create_dao_files(self, models):
        codes = {}
        for model in models:
            dao_code = self.generate_dao_class(model)
            codes[model.__name__] = dao_code
        return codes

    def auto_register_all_operations(self, models):
        for model in models:
            if inspect.isclass(model):
                if issubclass(model, DAOOperation) and not model == DAOOperation:
                    self.register_operation(model)


def __write_file(file_path, content):
    with open(file_path, "w",encoding="utf-8") as f:
        f.write(content)


def generate_dao_files(models_path: list[tuple[str, str]], output_path: str):
    # 增加当前目录到sys.path
    import sys
    sys.path.append(env.app_root)
    if not os.path.exists(output_path):
        os.makedirs(output_path)
    import importlib
    creator = DAOCreator()
    models = []
    for model_path, cls in models_path:
        model = importlib.import_module(model_path)
        model = getattr(model, cls)
        models.append(model)
    codes = creator.create_dao_files(models)
    for model_name, code in codes.items():
        if model_name.isalnum():
            pass
        model_name_snake = to_snake(model_name)
        file_path = os.path.join(output_path, f"{model_name_snake}_dao.py")
        __write_file(file_path, code)
    return codes
