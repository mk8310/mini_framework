from pydantic.alias_generators import to_snake

from mini_framework.databases.toolkit.generator_models.operator import DAOOperation


class Delete(DAOOperation):

    def func_name(self):
        return f"delete_{to_snake(self.model.__name__)}"

    def func_args(self):
        return f"{self.model.__name__.lower()}: {self.model.__name__}"

    def set_lines(self):
        self.lines = [
            f"session = await self.master_db()",
            f"await session.delete({self.model.__name__.lower()})"
        ]
