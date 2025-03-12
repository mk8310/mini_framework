"""
实现单例模式类装饰器
使用该装饰器的类在整个系统生命周期内将只有一个示例
需要确保线程、协程安全性
"""

from functools import wraps
from threading import Lock


def singleton(cls):
    """
    单例模式类装饰器
    :param cls:
    :return:
    """
    instances = {}
    lock = Lock()

    @wraps(cls)
    def wrapper(*args, **kwargs):
        if cls not in instances:
            with lock:
                if cls not in instances:
                    instances[cls] = cls(*args, **kwargs)
        return instances[cls]

    return wrapper
