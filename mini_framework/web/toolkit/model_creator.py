import datetime
from typing import Type, Any

from pydantic import Field
from sqlalchemy import Column, Integer, String, Float, Boolean, DateTime, Date

from mini_framework.databases.entities import BaseDBModel
from mini_framework.web.std_models.base_model import BaseViewModel


class ModelField(BaseViewModel):
    main_field: bool = Field(False, description="是否是主字段")
    name: str = Field(..., description="字段名")
    type: Type = Field(..., description="字段类型")
    default: Any = Field(None, description="默认值")
    description: str = Field("", description="字段描述")
    length: int = Field(0, description="字段长度")
    extra: dict = Field({}, description="额外参数")


def _validate_field_json(field_json: dict):
    """
    验证json是否是合法的字段描述
    :param field_json:
    :return:
    """
    required_keys = ["name", "type"]
    for key in required_keys:
        if key not in field_json:
            raise ValueError(f"字段描述中缺少必要属性：'{key}'")
    if not isinstance(field_json["name"], str):
        raise TypeError("字段名必须是字符串类型")
    if not isinstance(field_json["type"], type):
        raise TypeError("字段类型必须是有效的Python类型")


def _validate_db_model(fields: list[ModelField]):
    """
    验证数据库模型字段
    :param fields: 字段列表
    :return:
    """
    main_field_count = 0
    for field in fields:
        if field.main_field:
            main_field_count += 1
    if main_field_count < 1:
        raise ValueError("数据库模型必须至少有一个主字段")


py_type_to_sa_type = {
    int: Integer,
    str: String,
    float: Float,
    bool: Boolean,
    datetime.datetime: DateTime,
    datetime.date: Date,
}


def map_type_to_sa_type(py_type: Type[Any]):
    """
    将Python类型映射到SQLAlchemy类型
    :param py_type: Python类型
    :return:
    """
    if py_type in py_type_to_sa_type:
        return py_type_to_sa_type[py_type]
    else:
        raise ValueError(f"不支持的类型: {py_type}")


def generate_db_model_cls_name(table_name: str, prefix=""):
    """
    生成数据库模型类名
    :param prefix: 表名前缀
    :param table_name: 表名
    :return:
    """
    table_name = table_name.strip(prefix)
    return f"{table_name.capitalize()}"


class ModelCreator:
    def __init__(self):
        self.__fields: list[ModelField] = []

    @property
    def fields(self) -> list[ModelField]:
        return self.__fields

    def add_field(self, field_info: ModelField):
        """
        添加字段
        :param field_info: 字段信息
        :return:
        """
        self.__fields.append(field_info)

    def add_field_from_json(self, field_json: dict):
        """
        从json添加字段
        :param field_json: 字段的json描述
        :return:
        """
        _validate_field_json(field_json)
        field_info = ModelField(**field_json)
        self.add_field(field_info)

    def create_view_model(self, name: str) -> Type[BaseViewModel]:
        """
        动态创建视图模型
        :return:
        """

        namespace = {"__annotations__": {}}
        model = type(name, (BaseViewModel,), {})
        for field in self.__fields:
            field_name = field.name
            field_type = field.type
            field_default = field.default
            field_description = field.description
            field_extra = field.extra

            # 添加类型注解
            namespace["__annotations__"][field_name] = field_type

            field_args = {"description": field_description, **field_extra}

            # 设置字段的默认值和元数据
            if field_default is not ...:
                namespace[field_name] = Field(field_default, **field_args)
            else:
                namespace[field_name] = Field(..., **field_args)

            setattr(model, field_name, namespace[field_name])

        setattr(model, "__annotations__", namespace["__annotations__"])

        return model

    def create_db_model(self, table_name: str, prefix="") -> Type[BaseDBModel]:
        """
        动态创建数据库模型
        :param table_name: 表名
        :param prefix: 表名前缀
        :return:
        """
        _validate_db_model(self.__fields)
        attributes = {"__tablename__": table_name}
        for field in self.__fields:
            field_name = field.name
            field_type = field.type

            sa_column_type = map_type_to_sa_type(field_type)
            column_args = {}
            if field.default is not None:
                column_args["default"] = field.default
            if field.description:
                column_args["comment"] = field.description
            if field.main_field:
                column_args["primary_key"] = True
            column_args.update(field.extra)

            column = Column(sa_column_type, **column_args)
            attributes[field_name] = column

        cls_name = generate_db_model_cls_name(table_name, prefix)

        model = type(cls_name, (BaseDBModel,), attributes)

        return model
