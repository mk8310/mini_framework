import os
from mini_framework.commands.command_base import Command

from mini_framework.utils.modules import import_attr


class DOCGenerateCommand(Command):
    def __init__(self, metadata_model: str):
        """
        生成数据库模型的文档。
        :param metadata_model: 元数据模型变量路径，类似这样的："app.db.metadata"。
        """
        super().__init__()
        self.__metadata_model = metadata_model

    def run(self, output: str = None):
        """
        执行文档生成命令。根据元数据模型生成数据库模型文档。
        每个表之间目前没有明确的指出表与表之间的关系，在生成文档的时候按照类似这样的方式进行自动关联: student.id = class_member.student_id
        :param output: 生成的文件输出目录，相对于项目根目录。
        :return:
        """
        from mini_framework.databases.toolkit.doc_generator import DocGenerator
        from mini_framework.databases.toolkit.doc_generator import DocumentStructure

        output = output or "docs"
        metadata_model = import_attr(self.__metadata_model)
        from mini_framework.web.mini_app import app_config

        file_name = app_config.name.lower().replace(" ", "_").replace("-", "_")
        title = f"{app_config.title}数据库模型文档"
        doc_structure = DocumentStructure(
            title=app_config.title, file_name=f"{file_name}.docx"
        )
        doc_generator = DocGenerator(metadata_model, output, doc_structure)
        doc_file_path = doc_generator.create_word_document()
        from mini_framework.utils.log import logger

        logger.info(f"数据库模型文档已生成，输出目录：{doc_file_path}")
