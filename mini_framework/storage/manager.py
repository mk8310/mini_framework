import os
from datetime import timedelta, datetime
from ..utils.snowflake import SnowflakeIdGenerator
from minio import Minio as MinioClient
from urllib3 import BaseHTTPResponse

from mini_framework.design_patterns.singleton import singleton

from mini_framework.storage.errors import BucketNotFoundError
from mini_framework.storage.persistent.file_storage_dao import FileStorageDAO
from mini_framework.storage.persistent.models import FileStorage, FileState
from mini_framework.storage.view_model import FileStorageModel, FileStorageResponseModel
from mini_framework.utils.http import join_url_path


@singleton
class StorageManager:
    def __init__(self):
        from mini_framework.storage.config import storage_config

        self.__config = storage_config
        self.__client: MinioClient = MinioClient(
            self.__config.endpoint,
            access_key=self.__config.access_key,
            secret_key=self.__config.access_secret,
        )

    def query_put_object_url_with_token(self, file_storage: FileStorageModel) -> str:
        """
        查询文件上传路径（带 token）
        :param file_storage:
        :return: 文件上传路径
        """

        expires_time = timedelta(seconds=self.__config.token_expires_seconds)
        url = self.__client.get_presigned_url(
            "PUT",
            file_storage.storage_bucket,
            file_storage.file_path,
            expires=expires_time,
        )
        return url

    def query_get_object_url_with_token(self, file_storage: FileStorageModel) -> str:
        """
        查询文件下载路径（带 token）
        :param file_storage: FileStorageModel
        :return: 文件下载路径
        """
        url = self.__client.get_presigned_url(
            "GET",
            file_storage.storage_bucket,
            file_storage.file_path,
            expires=timedelta(seconds=self.__config.token_expires_seconds),
        )
        return url

    def get_object_data(self, virtual_bucket_key: str, filename: str):
        """
        读取远程文件内容
        :param virtual_bucket_key: 虚拟存储桶名称
        :param filename: 文件名
        :param path: 远程文件路径
        :return: 文件内容，二进制串
        """
        if virtual_bucket_key not in self.__config.virtual_buckets.keys():
            raise BucketNotFoundError(virtual_bucket_key)
        bucket = self.__config.virtual_buckets.get(virtual_bucket_key)
        file_path = join_url_path(bucket.path, filename)
        response: BaseHTTPResponse = None
        try:
            response = self.__client.get_object(bucket.bucket_name, file_path)
            return response.data
        finally:
            if response:
                response.close()
                response.release_conn()
        return None

    def download_file(
        self, virtual_bucket_key: str, remote_filename: str, local_filepath
    ) -> str:
        """
        下载文件到本地
        :param virtual_bucket_key: 虚拟桶名称
        :param remote_filename: 远程文件名
        :param local_filepath: 本地文件路径（含文件名）
        :return: 本地文件路径
        """
        if virtual_bucket_key not in self.__config.virtual_buckets.keys():
            raise BucketNotFoundError(virtual_bucket_key)
        bucket = self.__config.virtual_buckets.get(virtual_bucket_key)
        remote_file_path = join_url_path(bucket.path, remote_filename)
        self.__client.fget_object(bucket.bucket_name, remote_file_path, local_filepath)
        return local_filepath

    def put_file_to_object(
        self, virtual_bucket_key: str, remote_filename: str, local_filepath: str
    ):
        """
        上传文件到分布式存储
        :param virtual_bucket_key: 桶名称
        :param remote_filename: 远程文件名
        :param local_filepath: 本地文件路径（含文件名）
        :return:
        """
        if virtual_bucket_key not in self.__config.virtual_buckets.keys():
            raise BucketNotFoundError(virtual_bucket_key)
        file_size = os.path.getsize(local_filepath)
        bucket = self.__config.virtual_buckets.get(virtual_bucket_key)
        remote_file_path = join_url_path(bucket.path, remote_filename)
        self.__client.fput_object(bucket.bucket_name, remote_file_path, local_filepath)
        file_storage = FileStorageModel(
            file_name=remote_filename,
            virtual_bucket_name=bucket.key,
            file_size=file_size,
        )
        return file_storage

    async def add_file(
        self, file_storage_dao: FileStorageDAO, file_storage: FileStorageModel
    ) -> FileStorageResponseModel:
        """
        新增文件
        :param file_storage_dao:
        :param file_storage:
        :return:
        """
        file_storage_db = FileStorage()
        file_storage_db.file_id = SnowflakeIdGenerator().generate_id()
        file_storage_db.virtual_bucket_name = file_storage.virtual_bucket_name
        file_storage_db.file_path = file_storage.file_path
        file_storage_db.file_name = file_storage.file_name
        file_storage_db.file_type = file_storage.file_type
        file_storage_db.file_size = file_storage.file_size
        file_storage_db.state = FileState.wait.value
        file_storage_db.created_at = datetime.now()
        file_storage_db.create_with = "system"
        result = await file_storage_dao.add_file(file_storage_db)
        upload_uri = self.query_put_object_url_with_token(file_storage)
        download_uri = self.query_get_object_url_with_token(file_storage)
        resp = FileStorageResponseModel(
            file_id= str(result.file_id) if isinstance(result.file_id, int) else  result.file_id,
            virtual_bucket_name=result.virtual_bucket_name,
            file_name=file_storage.file_name,
            file_type=file_storage.file_type,
            upload_url=upload_uri,
            download_url=download_uri,
        )
        return resp


storage_manager = StorageManager()
