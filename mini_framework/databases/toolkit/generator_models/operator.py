from sqlalchemy import inspect


class DAOOperation:
    def __init__(self, model):
        self.model = model
        self.lines = []

    def generate_code(self):
        self.set_lines()
        body = "\n".join([f"\t\t{line}" for line in self.lines])
        return f"\n\t{self.__func_declare()}\n{body}\n"

    def primary_key_fields(self):
        """ Extract the primary key field names from the model """
        primary_keys = inspect(self.model).primary_key
        return [key.name for key in primary_keys]

    def func_name(self):
        raise NotImplementedError("Subclasses must implement this method.")

    def func_args(self):
        raise NotImplementedError("Subclasses must implement this method.")

    def __func_declare(self):
        return f"async def {self.func_name()}(self, {self.func_args()}):"

    def set_lines(self):
        raise NotImplementedError("Subclasses must implement this method.")

    def __repr__(self):
        return f"{self.__class__.__name__}({self.model.__name__})"
