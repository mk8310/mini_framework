from mini_framework.design_patterns.singleton import singleton


class VirtualBucketConfig:
    def __init__(self, key, bucket_config: dict):
        """
        虚拟存储桶配置
        :param key: 虚拟存储桶的key
        :param bucket_config: 存储桶配置
        """
        self.__key = key
        self.__bucket_name = bucket_config.get("name")
        self.__path = bucket_config.get("path", "/")

    @property
    def key(self):
        """
        虚拟存储桶的key
        :return:
        """
        return self.__key

    @property
    def bucket_name(self):
        """
        物理存储桶名称
        :return:
        """
        return self.__bucket_name

    @property
    def path(self):
        """
        在存储桶中的路径
        :return:
        """
        return self.__path


@singleton
class StorageConfig:
    def __init__(self):
        """
        存储配置
        """
        from mini_framework.configurations import config_injection

        manager = config_injection.get_config_manager()
        storage_dict = manager.get_domain_config("storage")
        if not storage_dict:
            return
        self.__endpoint = storage_dict.get("endpoint")
        self.__access_key = storage_dict.get("access_key")
        self.__access_secret = storage_dict.get("secret_key")
        self.__token_exp_sec = storage_dict.get("token_exp_sec")
        buckets = storage_dict.get("buckets")
        self.__buckets = {}
        if buckets:
            for key, value in buckets.items():
                self.__buckets[key] = VirtualBucketConfig(key, value)

    @property
    def endpoint(self):
        """
        存储服务的endpoint
        :return:
        """
        return self.__endpoint

    @property
    def access_key(self):
        """
        存储服务的access_key
        :return:
        """
        return self.__access_key

    @property
    def access_secret(self):
        """
        存储服务的access_secret
        :return:
        """
        return self.__access_secret

    @property
    def token_expires_seconds(self):
        """
        token的过期时间
        :return:
        """
        return self.__token_exp_sec

    @property
    def virtual_buckets(self):
        """
        虚拟存储桶配置
        :return:
        """
        return self.__buckets


storage_config = StorageConfig()
