import importlib
import inspect
import logging
import os
import shutil
import subprocess
from enum import Enum

from alembic import command
from alembic.config import Config
from alembic.operations import MigrationScript
from alembic.operations.ops import ExecuteSQLOp
from jinja2 import Environment, FileSystemLoader
from sqlalchemy import insert, update, delete

from mini_framework.context import env
from mini_framework.utils.modules import import_attr


class MigrationOperator(str, Enum):
    upgrade = 'upgrade'
    downgrade = 'downgrade'
    revision = 'revision'
    init = 'init'


def detect_model_table_exists(model, session):
    """检测模型对应的表是否存在"""
    return session.connection().engine.dialect.has_table(session.connection(), model.__tablename__)


def _generate_insert_sql(model, existing_keys, primary_keys, seed_data, insert_data):
    """
    生成插入数据的SQL语句
    :param model:
    :param existing_keys:
    :param primary_keys:
    :param seed_data:
    :param insert_data:
    :return:
    """
    for data in seed_data:
        key_tuple = tuple(data[pk] for pk in primary_keys)
        if key_tuple not in existing_keys:
            insert_data.append(data)


def generate_sql(stmt, engine):
    """
    根据SQLAlchemy语句生成SQL
    :param stmt:
    :param engine:
    :return:
    """
    dialect = engine.dialect
    compiled = stmt.compile(dialect=dialect, compile_kwargs={"literal_binds": True})
    return str(compiled)


def process_model(model, seed_method, session, script: MigrationScript):
    """生成并添加数据操作命令到迁移脚本中"""
    # 获取种子数据
    seed_model_data = seed_method()
    from mini_framework.databases.entities import to_dict
    seed_data = [to_dict(item) for item in seed_model_data]
    # 数据对比和生成SQL语句
    insert_data = []
    update_statements = []
    delete_statements = []

    # 查询现有数据
    primary_keys = [key.name for key in model.__table__.primary_key]
    if not detect_model_table_exists(model, session):
        _generate_insert_sql(model, set(), primary_keys, seed_data, insert_data)
    else:
        existing_records = session.query(model).all()
        existing_data = {tuple(getattr(record, pk) for pk in primary_keys): record for record in existing_records}

        existing_keys = set(existing_data.keys())
        seed_keys = {tuple(data[pk] for pk in primary_keys) for data in seed_data}

        _generate_insert_sql(model, existing_keys, primary_keys, seed_data, insert_data)

        # Generate UPDATE statements
        for key_tuple in (existing_keys & seed_keys):
            existing_record = existing_data[key_tuple]
            seed_record = next(item for item in seed_data if tuple(item[pk] for pk in primary_keys) == key_tuple)

            updates = {k: v for k, v in seed_record.items() if
                       getattr(existing_record, k) != v and k not in primary_keys}
            # updates = ', '.join(f"{k} = '{v}'" if isinstance(v, str) else f"{k} = {v}"
            #                     for k, v in seed_record.items()
            #                     if getattr(existing_record, k) != v and k not in primary_keys)

            if updates:
                # where_clause = ' AND '.join(f"{pk} = '{getattr(existing_record, pk)}'" for pk in primary_keys)
                # update_statements.append(f"UPDATE {model.__tablename__} SET {updates} WHERE {where_clause};")
                stmt = update(model).where(
                    *[getattr(model, pk) == getattr(existing_record, pk) for pk in primary_keys]
                ).values(updates)
                update_statements.append(generate_sql(stmt, session.connection().engine))

        # Generate DELETE statements
        for key_tuple in (existing_keys - seed_keys):
            stmt = delete(model).where(
                *[getattr(model, pk) == getattr(existing_data[key_tuple], pk) for pk in primary_keys]
            )
            delete_statements.append(generate_sql(stmt, session.connection().engine))
            # where_clause = ' AND '.join(f"{pk} = '{getattr(existing_data[key_tuple], pk)}'" for pk in primary_keys)
            # delete_statements.append(f"DELETE FROM {model.__tablename__} WHERE {where_clause};")
    for data in insert_data:
        # columns = ', '.join(data.keys())
        # values = ', '.join(f"'{v}'" if isinstance(v, str) else str(v) for v in data.values())
        # sql_op = ExecuteSQLOp(f"INSERT INTO {model.__tablename__} ({columns}) VALUES ({values});")
        stmt = insert(model).values(data)
        sql_op = ExecuteSQLOp(generate_sql(stmt, session.connection().engine))
        script.upgrade_ops.ops.append(sql_op)
    for stmt in update_statements:
        script.upgrade_ops.ops.append(ExecuteSQLOp(stmt))
    for stmt in delete_statements:
        script.downgrade_ops.ops.append(ExecuteSQLOp(stmt))


def clean_alembic_version_table(engine):
    """删除 Alembic 版本表中的所有记录"""
    from sqlalchemy import Table
    from sqlalchemy import MetaData
    metadata = MetaData()
    metadata.reflect(bind=engine)

    if 'alembic_version' in metadata.tables:
        alembic_version: Table = metadata.tables['alembic_version']
        alembic_version.drop(engine, checkfirst=True)

        print("All records in alembic_version table have been deleted.")
    else:
        print("Alembic version table does not exist.")


def clean_migration_scripts(migration_dir, config_path):
    """删除迁移脚本目录中的所有文件"""
    if os.path.exists(migration_dir):
        shutil.rmtree(migration_dir)
        print(f"All migration scripts in {migration_dir} have been deleted.")

    if os.path.exists(config_path):
        os.remove(config_path)
        print(f"Config file {config_path} has been deleted.")


class MigrationTool:
    def __init__(self, metadata_package_path, db_key: str):
        self.metadata_package_path = metadata_package_path
        self.base_path = env.app_root
        self.alembic_path = os.path.join(env.app_root, 'alembic')
        self.versions_path = os.path.join(self.alembic_path, 'versions')
        self.config_path = os.path.join(self.base_path, 'alembic.ini')
        from mini_framework.databases.config import db_config
        physic_db_config = db_config.get_database(db_key)
        self.config = Config(self.config_path)
        self.config.set_main_option("script_location", "alembic")
        self.config.set_main_option("exclude_tables", "alembic_version, dual")
        self.sqlalchemy_url = physic_db_config.master.sync_database_uri
        self.config.set_main_option("sqlalchemy.url", self.sqlalchemy_url)
        self.metadata_package = metadata_package_path.rsplit('.', 1)[0]
        self.metadata_member = metadata_package_path.split('.')[-1]
        self.db_key = db_key
        # 动态加载 metadata
        self.metadata = import_attr(metadata_package_path)
        env.set("database_url", self.sqlalchemy_url)

    def upgrade(self, revision='head'):
        """升级到最新的版本或指定的版本"""
        self.config.attributes['configure_logger'] = False
        self.config.attributes['target_metadata'] = self.metadata
        self.config.attributes['script_location'] = self.alembic_path
        command.upgrade(self.config, revision)

    def downgrade(self, revision='-1'):
        """降级到前一个版本或指定的版本"""
        self.config.attributes['configure_logger'] = False
        self.config.attributes['target_metadata'] = self.metadata
        command.downgrade(self.config, revision)

    def revision(self, message):
        """生成迁移脚本"""

        def process_revision_directives(context, revision, directives):
            script = directives[0]
            if script.upgrade_ops.is_empty():
                return

            from mini_framework.databases.conn_managers.db_manager import db_connection_manager
            session = db_connection_manager.get_sync_session(self.db_key, True)

            # 动态加载所有模型
            try:
                metadata_package = importlib.import_module(self.metadata_package)
                members = inspect.getmembers(metadata_package, inspect.ismodule)
                for module in members:
                    for _, model in inspect.getmembers(module[1], inspect.isclass):
                        if not hasattr(model, '__table__'):  # 确保是一个 SQLAlchemy 模型
                            continue
                        seed_method = getattr(model, 'seed', None)
                        if callable(seed_method):
                            process_model(model, seed_method, session, script)
            except Exception as e:
                logging.error(f"Error processing models: {e}")
            finally:
                session.close()

        self.config.attributes['configure_logger'] = False
        self.config.attributes['target_metadata'] = self.metadata
        command.revision(self.config, message=message, autogenerate=True,
                         process_revision_directives=process_revision_directives)
        self.git_add_commit(message)

    def __clear_alembic(self):
        """清空 alembic 目录及 alembic 版本表"""
        from mini_framework.databases.conn_managers.db_manager import db_connection_manager
        session = db_connection_manager.get_sync_session(self.db_key, True)
        clean_alembic_version_table(session.connection().engine)
        clean_migration_scripts(self.alembic_path, self.config_path)

    def init(self):
        """初始化 alembic"""
        self.__clear_alembic()
        self.config.attributes['configure_logger'] = False
        self.config.attributes['target_metadata'] = self.metadata
        command.init(self.config, 'alembic')

        templates_path = os.path.join(os.path.dirname(__file__), 'templates')
        jinja2_env = Environment(loader=FileSystemLoader(templates_path))
        os.makedirs(self.alembic_path, exist_ok=True)
        os.makedirs(self.versions_path, exist_ok=True)

        alembic_ini_template = jinja2_env.get_template('alembic_ini_template.j2')
        env_py_template_j2 = jinja2_env.get_template('env_py_template.j2')

        with open(os.path.join(self.base_path, 'alembic.ini'), 'w') as f:
            f.write(alembic_ini_template.render(script_location=self.alembic_path, sqlalchemy_url=self.sqlalchemy_url))

        metadata_import_stmt = f"from {self.metadata_package} import {self.metadata_member}"
        metadata_stmt = f"target_metadata = {self.metadata_member}"
        with open(os.path.join(self.alembic_path, 'env.py'), 'w') as f:
            f.write(env_py_template_j2.render(metadata_import_stmt=metadata_import_stmt, metadata_stmt=metadata_stmt))

        self.git_add_commit("Init alembic")

    def git_add_commit(self, message):
        """将新生成的迁移脚本加入到Git仓库并提交"""
        # 暂存所有变更
        subprocess.run(["git", "add", "."], cwd=self.alembic_path)
        subprocess.run(["git", "add", "../alembic.ini"], cwd=self.alembic_path)
        # 提交变更
        commit_message = f"Add new migration: {message}"
        # subprocess.run(["git", "commit", "-m", commit_message], cwd=self.alembic_path)
        logging.info(f"Commit message: {commit_message}")
