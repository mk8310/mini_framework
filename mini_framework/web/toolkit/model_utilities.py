from typing import Type, TypeVar

from mini_framework.databases.entities import BaseDBModel, to_dict
from mini_framework.web.std_models.base_model import BaseViewModel

ViewModelT = TypeVar('ViewModelT', bound=BaseViewModel)
BaseDBModelT = TypeVar('BaseDBModelT', bound=BaseDBModel)


def orm_model_to_view_model(orm_model: BaseDBModel, view_model_cls: Type[ViewModelT],
                            other_mapper: dict[str, str] = None, exclude: list = None) -> ViewModelT:
    """
    ORM模型转换为视图模型
    """
    data_dict = to_dict(orm_model)
    view_model_keys = view_model_cls.model_fields.keys()
    data_keys = list(data_dict.keys())
    for data_key, view_model_key in other_mapper.items() if other_mapper else {}:
        if data_key in data_keys:
            data_dict[view_model_key] = data_dict[data_key]
            # data_dict.pop(data_key)
    for data_key in data_keys:
        if data_key not in view_model_keys or (exclude and data_key in exclude):
            data_dict.pop(data_key)
    view_model = view_model_cls(**data_dict)
    # for field in view_model_cls.__fields__.keys():
    #     setattr(view_model, field, getattr(orm_model, field))
    return view_model


def view_model_to_orm_model(view_model: BaseViewModel, orm_model_cls: Type[BaseDBModelT],
                            other_mapper: dict[str, str] = None,
                            exclude: list = None) -> BaseDBModelT:
    """
    视图模型转换为ORM模型
    @param view_model: 视图模型
    @param orm_model_cls: ORM模型
    @param other_mapper: 其他属性映射
    @param exclude: 排除字段
    """
    data_dict = view_model.model_dump()
    orm_model = orm_model_cls()
    for view_model_key, data_key in other_mapper.items() if other_mapper else {}:
        if view_model_key in data_dict:
            data_dict[data_key] = data_dict[view_model_key]
            data_dict.pop(view_model_key)
    data_keys = list(data_dict.keys())
    for key in data_keys:
        if exclude and key in exclude:
            data_dict.pop(key)
    for key, value in data_dict.items():
        setattr(orm_model, key, value)
    return orm_model
