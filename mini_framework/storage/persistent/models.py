from datetime import datetime
from enum import Enum

from sqlalchemy import BigInteger
from sqlalchemy.orm import Mapped, mapped_column

from mini_framework.databases.entities import BaseDBModel


class FileState(str, Enum):
    """
    文件状态, wait: 等待上传, uploading: 上传中, uploaded: 已上传, failed: 上传失败
    """

    wait = "wait"
    uploading = "uploading"
    uploaded = "uploaded"
    failed = "upload_failed"


class FileStorage(BaseDBModel):
    __tablename__ = "file_storage"
    __table_args__ = {"comment": "文件存储表"}

    # 文件ID需要为bigint
    file_id: Mapped[int] = mapped_column(BigInteger, primary_key=True, comment="文件ID")
    file_name: Mapped[str] = mapped_column(comment="文件名")
    file_path: Mapped[str] = mapped_column(comment="文件路径")
    virtual_bucket_name: Mapped[str] = mapped_column(comment="虚拟存储桶名称")
    file_size: Mapped[int] = mapped_column(comment="文件大小")
    file_type: Mapped[str] = mapped_column(comment="文件类型")
    state: Mapped[str] = mapped_column(comment="状态")
    created_at: Mapped[datetime] = mapped_column(comment="创建时间")
    create_with: Mapped[str] = mapped_column(comment="创建人")
