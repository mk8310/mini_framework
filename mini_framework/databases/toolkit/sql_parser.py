import sqlparse
from sqlparse.sql import (
    IdentifierList,
    Identifier,
    Function,
    Parenthesis,
    Case,
    TokenList,
)
from sqlparse.tokens import Keyword, DML, Whitespace, Comment


class SQLParser:
    def __init__(self, sql):
        self.__sql = sql

    def parse_select_fields(self):
        """
        解析 SQL 查询语句中的输出字段
        :return: 输出字段列表
        """
        # 解析 SQL 语句
        parsed = sqlparse.parse(self.__sql)
        if not parsed:
            return []

        stmt = parsed[0]

        # 检查语句类型是否为 SELECT
        if stmt.get_type() != "SELECT":
            raise Exception("The SQL statement is not a SELECT query.")

        # 初始化输出字段列表
        output_fields = []

        # 标记是否进入 SELECT 子句
        select_clause = False

        # 遍历 tokens 以提取输出字段
        for token in stmt.tokens:
            # 跳过空白和注释
            if token.ttype in (Whitespace, Comment.Single, Comment.Multiline):
                continue

            # 检查 SELECT 关键字
            if token.ttype is DML and token.value.upper() == "SELECT":
                select_clause = True
                continue

            # 如果遇到 FROM，则停止解析
            if token.ttype is Keyword and token.value.upper() == "FROM":
                break

            # 在 SELECT 子句中，提取字段
            if select_clause:
                if isinstance(token, IdentifierList):
                    for identifier in token.get_identifiers():
                        field_name = identifier.get_alias() or identifier.get_name()
                        output_fields.append(field_name)
                elif isinstance(token, Identifier):
                    field_name = token.get_alias() or token.get_name()
                    output_fields.append(field_name)
                elif isinstance(token, Function):
                    # 处理没有别名的函数
                    field_name = token.get_alias() or token.get_name()
                    output_fields.append(field_name)
                elif isinstance(token, Parenthesis):
                    # 处理子查询
                    field_name = token.get_alias() or token.get_name()
                    output_fields.append(field_name)
                elif token.ttype is Keyword:
                    # 处理 SELECT 子句中的关键字
                    continue

        return output_fields
