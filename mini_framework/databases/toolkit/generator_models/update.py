from pydantic.alias_generators import to_snake

from mini_framework.databases.toolkit.generator_models.operator import DAOOperation


class Update(DAOOperation):

    def func_name(self):
        return f"update_{to_snake(self.model.__name__)}"

    def func_args(self):
        return f"{self.model.__name__.lower()}, *args, is_commit=True"

    def set_lines(self):
        class_name = self.model.__name__
        primary_keys = self.primary_key_fields()
        where_condition = " and ".join(
            f"{class_name}.{field} == {class_name.lower()}.{field}" for field in primary_keys)
        self.lines = [
            f"session = await self.master_db()",
            f"update_contents = get_update_contents({class_name.lower()}, *args)",
            f"query = update({class_name}).where({where_condition}).values(**update_contents)",
            f"return await self.update(session, query, {class_name.lower()}, update_contents, is_commit=is_commit)"
        ]
