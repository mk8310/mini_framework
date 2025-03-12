from pydantic.alias_generators import to_snake

from mini_framework.databases.toolkit.generator_models.operator import DAOOperation


class GetByID(DAOOperation):

    def func_name(self):
        class_name = self.model.__name__
        pk_fields = self.primary_key_fields()
        pk_fields_names = "_and".join(f"{field}" for field in pk_fields)
        return f"get_{to_snake(class_name)}_by_{pk_fields_names}"

    def func_args(self):
        pk_fields = self.primary_key_fields()
        return ", ".join(f"{field}" for field in pk_fields)

    def set_lines(self):
        class_name = self.model.__name__
        pk_fields = self.primary_key_fields()

        where_clause = " and ".join(f"{class_name}.{field} == {field}" for field in pk_fields)
        self.lines = [
            f"session = await self.slave_db()",
            f"result = await session.execute(select({class_name}).where({where_clause}))",
            f"return result.scalar_one_or_none()"
        ]
