from sqlalchemy import select

from mini_framework.databases.entities.dao_base import DAOBase
from mini_framework.storage.persistent.models import FileStorage
from mini_framework.web.std_models.page import PageRequest


class FileStorageDAO(DAOBase):
    async def add_file(self, file_storage: FileStorage):
        """
        新增文件
        :param file_storage:
        :return:
        """
        session = await self.master_db()
        session.add(file_storage)
        return file_storage

    async def get_file_by_id(self, file_id):
        """
        通过文件ID获取文件
        :param file_id:
        :return:
        """
        session = await self.slave_db()
        result = await session.execute(
            select(FileStorage).filter(FileStorage.file_id == file_id)
        )
        return result.first()

    async def get_file_by_name(self, virtual_bucket, file_path, file_name):
        """
        通过文件名获取文件
        :param virtual_bucket: 虚拟存储桶名称
        :param file_path: 文件路径
        :param file_name: 文件名
        :return:
        """
        session = await self.slave_db()
        result = await session.execute(
            select(FileStorage).filter(
                FileStorage.virtual_bucket_name == virtual_bucket,
                FileStorage.file_path == file_path,
                FileStorage.file_name == file_name,
            )
        )
        return result.first()

    async def query_file_list_page(
        self,
        virtual_bucket: str,
        file_path: str,
        file_name: str,
        file_type: str,
        file_size_min: int,
        file_size_max: int,
        created_at_start: str,
        created_at_end: str,
        page_request: PageRequest,
    ):
        """
        分页查询文件列表
        :param page_request: 分页请求
        :param virtual_bucket:  存储桶名称
        :param file_path:  文件路径
        :param file_name: 文件名
        :param file_type: 文件类型
        :param file_size_min: 文件大小最小值
        :param file_size_max: 文件大小最大值
        :param created_at_start: 创建时间起始
        :param created_at_end: 创建时间结束
        :return:
        """
        query = select(FileStorage)
        if virtual_bucket:
            query = query.filter(FileStorage.virtual_bucket_name == virtual_bucket)
        if file_path:
            query = query.filter(FileStorage.file_path == file_path)
        if file_name:
            query = query.filter(FileStorage.file_name.like(f"%{file_name}%"))
        if file_type:
            query = query.filter(FileStorage.file_type == file_type)
        if file_size_min:
            query = query.filter(FileStorage.file_size >= file_size_min)
        if file_size_max:
            query = query.filter(FileStorage.file_size <= file_size_max)
        if created_at_start:
            query = query.filter(FileStorage.created_at >= created_at_start)
        if created_at_end:
            query = query.filter(FileStorage.created_at <= created_at_end)
        query = query.order_by(FileStorage.created_at.desc())
        return await self.query_page(query, page_request)
