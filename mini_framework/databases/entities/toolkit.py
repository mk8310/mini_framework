from typing import List
from sqlalchemy import Row, inspect
from .declaritives import BaseDBModel


def to_dict(
        result,
        id_replace=None,
        value_list=None,
        null_to_str: list = None,
        pop_list: list = None,
):
    """
    将model转换为dict
    :param result: model对象
    :param id_replace: id替换的key
    :param value_list: 需要的key列表
    :param null_to_str: 需要将None转换为''的key列表
    :param pop_list: 需要删除的key列表
    :return:
    """
    if value_list is None:
        value_list = []
    if pop_list is None:
        pop_list = []
    if not result:
        return {}
    dict_obj = result
    if isinstance(result, Row):
        dict_obj = result._asdict()
        # dict_obj = {key: result[key] for key in result._asdict().keys()}
    elif not isinstance(result, dict):
        # 使用 inspect 来获取模型的所有属性
        mapper = inspect(result)
        # 访问所有的模型属性
        dict_obj = {attr.key: getattr(result, attr.key) for attr in mapper.attrs}

    if "_sa_instance_state" in dict_obj:
        del dict_obj["_sa_instance_state"]
    if value_list:
        dict_obj_tmp = dict()
        # 使用for循环可以保证dict转json后key的顺序和value_list里key的顺序一致
        for key_need in value_list:
            dict_obj_tmp.update(
                {key_need: dict_obj.get(key_need)} if key_need in dict_obj else {}
            )
        dict_obj = dict_obj_tmp
    if id_replace and "id" in dict_obj:
        dict_obj[id_replace] = dict_obj["id"]
        del dict_obj["id"]
    if null_to_str:
        for key in null_to_str:
            if key in dict_obj.keys():
                if not dict_obj[key]:
                    dict_obj[key] = ""
    for pop_key in pop_list:
        if pop_key in dict_obj:
            del dict_obj[pop_key]
    return dict_obj


def to_dicts(
        models: List[BaseDBModel],
        id_replace=None,
        value_list=None,
        null_to_str: list = None,
        pop_list: list = None,
):
    """
    将model列表转换为dict列表
    :param models: model列表
    :param id_replace: id替换的key
    :param value_list: 需要的key列表
    :param null_to_str: 需要将None转换为''的key列表
    :param pop_list: 需要删除的key列表
    :return:
    """
    if value_list is None:
        value_list = []
    if not models:
        return []
    return [
        to_dict(
            model, id_replace, value_list, null_to_str=null_to_str, pop_list=pop_list
        )
        for model in models
    ]
