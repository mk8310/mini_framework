import importlib


def import_callable(module_path: str):
    """
    在模块中导入可调用对象。
    :param module_path:
    :return:
    """
    try:
        package = module_path.rsplit(".", 1)[0]
        module_name = module_path.rsplit(".", 1)[1]
        module = importlib.import_module(package)
        result = getattr(module, module_name)
        if not callable(result):
            raise ValueError(f"Module {module_path} is not callable.")
        return result
    except ModuleNotFoundError as ex:
        from ..utils.log import logger
        logger.error(f"Module {module_path} import failed: {ex}")
        return


def import_module(module_path: str):
    """
    在模块中导入模块。
    :param module_path:
    :return:
    """
    try:
        return importlib.import_module(module_path)
    except ModuleNotFoundError as ex:
        from ..utils.log import logger
        logger.error(f"Module {module_path} import failed: {ex}")
        return


def import_class(module_path: str):
    """
    在文件中导入类。
    :param module_path: 模块路径
    :return:
    """
    try:
        package = module_path.rsplit(".", 1)[0]
        class_name = module_path.rsplit(".", 1)[1]
        module = importlib.import_module(package)
        result = getattr(module, class_name)
        if not isinstance(result, type):
            raise ValueError(f"Module {module_path} is not a class.")
        return result
    except ModuleNotFoundError as ex:
        from ..utils.log import logger
        logger.error(f"Module {module_path} import failed: {ex}")
        return


def import_attr(module_path: str):
    """
    在文件中导入属性。
    :param module_path: 模块路径
    :return:
    """
    try:
        package = module_path.rsplit(".", 1)[0]
        attr_name = module_path.rsplit(".", 1)[1]
        module = importlib.import_module(package)
        result = getattr(module, attr_name)
        return result
    except ModuleNotFoundError as ex:
        from ..utils.log import logger
        logger.error(f"Module {module_path} import failed: {ex}")
        return
