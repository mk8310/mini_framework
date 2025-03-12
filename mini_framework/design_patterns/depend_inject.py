"""
实现依赖注入，需要依赖注入的类继承该类
"""
from dataclasses import dataclass


def dataclass_inject(cls):
    """
    依赖注入装饰器
    :param cls: 需要实现注入的类，该类将自动装饰为dataclass
    :return: 装饰后的类
    """
    from injector import inject as third_party_inject
    cls = dataclass(cls)  # 首先应用dataclass装饰器
    cls = third_party_inject(cls)  # 然后应用inject装饰器
    return cls


def get_injector(cls):
    """
    获取注入实例
    :param cls: 需要获取的类
    :return: 实例
    """
    from injector import Injector
    injector = Injector()
    instance = injector.get(cls)
    return instance
