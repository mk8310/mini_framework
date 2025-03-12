import os

from mini_framework.commands.command_base import Command
from mini_framework.context import env


class DAOGenerateCommand(Command):
    def __init__(self, model_list: list[tuple[str, str]]):
        super().__init__()
        self.__model_list = model_list

    def run(self, model_list: list[tuple[str, str]], output: str = "daos_test"):
        """
        生成DAO代码文件。
        :param model_list: 数据库模型列表。
        :param output: 生成的文件输出目录。
        :return:
        """
        env.sync_type = "sync"
        dao_files_path = os.path.join(env.app_root, output)
        from mini_framework.databases.toolkit.dao_generator import generate_dao_files
        generate_dao_files(self.__model_list, dao_files_path)
