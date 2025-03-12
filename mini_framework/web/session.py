from mini_framework.cache.manager import redis_client_manager


class Session(object):
    def __init__(self, unique_key: str):
        self.__session_cache = redis_client_manager.get_client("session")
        self.__unique_key = unique_key

    def __setitem__(self, key, value):
        self.__session_cache.hset(self.__unique_key, key, value)

    def __getitem__(self, key):
        return self.__session_cache.hget(self.__unique_key, key)

    def __delitem__(self, key):
        self.__session_cache.hdel(self.__unique_key, key)

    def __contains__(self, key):
        return self.__session_cache.hexists(self.__unique_key, key)

    def __iter__(self):
        return iter(self.__session_cache.hkeys(self.__unique_key))

    def __len__(self):
        return self.__session_cache.hlen(self.__unique_key)
