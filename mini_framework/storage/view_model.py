from pydantic import Field

from mini_framework.storage.errors import BucketNotFoundError
from mini_framework.utils.http import join_url_path
from mini_framework.web.std_models.base_model import BaseViewModel


class FileStorageModel(BaseViewModel):
    file_name: str = Field(..., title="文件名", description="文件名")
    virtual_bucket_name: str = Field(
        ..., title="虚拟存储桶名称", description="虚拟存储桶名称"
    )
    file_size: int = Field(..., title="文件大小", description="文件大小, 单位字节")

    @property
    def file_path(self):
        """
        获取文件路径,不包含存储桶名称
        :return:
        """
        from mini_framework.storage.config import storage_config

        virtual_bucket_config = storage_config.virtual_buckets.get(
            self.virtual_bucket_name, None
        )
        if virtual_bucket_config is None:
            raise BucketNotFoundError(self.virtual_bucket_name)
        file_path = join_url_path(
            virtual_bucket_config.path,
            self.file_name,
        )
        return file_path

    @property
    def full_file_path(self):
        """
        获取完整文件路径,包含存储桶名称
        :return:
        """
        from mini_framework.storage.config import storage_config

        virtual_bucket_config = storage_config.virtual_buckets.get(
            self.virtual_bucket_name, None
        )
        if virtual_bucket_config is None:
            raise BucketNotFoundError(self.virtual_bucket_name)
        file_path = join_url_path(
            virtual_bucket_config.virtual_bucket_name,
            virtual_bucket_config.path,
            self.file_name,
        )
        return file_path

    @property
    def file_type(self):
        """
        获取文件类型
        :return:
        """
        return self.file_name.split(".")[-1]

    @property
    def storage_bucket(self):
        """
        获取物理存储桶名称
        :return:
        """
        from mini_framework.storage.config import storage_config

        bucket_config = storage_config.virtual_buckets.get(
            self.virtual_bucket_name, None
        )
        if bucket_config is None:
            raise BucketNotFoundError(self.virtual_bucket_name)
        return bucket_config.bucket_name


class FileStorageResponseModel(BaseViewModel):
    file_id: int|str = Field(..., title="文件ID", description="文件ID")
    file_name: str = Field(..., title="文件名", description="文件名")
    file_type: str = Field(..., title="文件类型", description="文件类型")
    upload_url: str = Field(..., title="文件URL", description="文件URL")
    download_url: str = Field(..., title="下载URL", description="下载URL")
    virtual_bucket_name: str = Field(..., title="存储桶名称", description="存储桶名称")
