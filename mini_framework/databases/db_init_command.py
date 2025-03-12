from mini_framework.commands.command_base import Command
from mini_framework.context import env
from mini_framework.databases.version.migrations import MigrationTool, MigrationOperator


class DatabaseInitCommand(Command):
    def __init__(self, metadata_model):
        self.__metadata_model = metadata_model
        super().__init__()

    def run(self, operation: MigrationOperator = MigrationOperator.upgrade, db_key="default", message="",
            reversion="head"):
        """
        初始化数据库结构。
        :param message: 提交版本信息。
        :param db_key: 数据库连接编码。
        :param reversion: 回退版本，head 表示最新版本，-1 表示上一个版本，其他版本号表示指定版本。默认为 head。
        :param operation: 操作类型，upgrade 或 downgrade。
        :return:
        """
        env.sync_type = "sync"
        migration_tool = MigrationTool(self.__metadata_model, db_key)
        if operation == MigrationOperator.init:
            # 需要用户确认是否继续操作
            confirmation = input("当前操作将会导致所有数据库版本被清空，是否继续执行？ (y/n): ")
            if confirmation.lower() != 'y':
                print("Operation cancelled.")
                return
            migration_tool.init()
        elif operation == MigrationOperator.revision:
            migration_tool.revision(message)
        elif operation == MigrationOperator.upgrade:
            migration_tool.upgrade()
        elif operation == MigrationOperator.downgrade:
            migration_tool.downgrade()
