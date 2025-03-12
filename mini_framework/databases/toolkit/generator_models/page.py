from pydantic.alias_generators import to_snake

from mini_framework.databases.toolkit.generator_models.operator import DAOOperation


class QueryWithPage(DAOOperation):

    def func_name(self):
        return f"query_{to_snake(self.model.__name__)}_with_page"

    def func_args(self):
        return f"pageQueryModel, page_request: PageRequest"

    def set_lines(self):
        class_name = self.model.__name__
        self.lines = [f"query = select({class_name})"]
        self.lines.append("")
        self.lines.append(f"### 此处填写查询条件")
        self.lines.append("")
        self.lines.append(f"paging = await self.query_page(query, page_request)")
        self.lines.append("return paging")
