from mini_framework.web.std_models.errors import MiniHTTPException


class BucketNotFoundError(MiniHTTPException):
    def __init__(self, bucket_name: str):
        super().__init__(
            404,
            "BUCKET_NOT_FOUND",
            f"bucket {bucket_name} not found.",
            f"存储桶{bucket_name}不存在"
        )
