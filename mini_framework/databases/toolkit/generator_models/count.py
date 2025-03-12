from pydantic.alias_generators import to_snake

from mini_framework.databases.toolkit.generator_models.operator import DAOOperation


class Count(DAOOperation):
    def func_name(self):
        return f"get_{to_snake(self.model.__name__)}_count"

    def func_args(self):
        return ""

    def set_lines(self):
        self.lines = [
            f"session = await self.slave_db()",
            f"result = await session.execute(select(func.count()).select_from({self.model.__name__}))",
            f"return result.scalar()"
        ]
