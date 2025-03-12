from mini_framework.authentication.persistent.jwt_daos import JwtDAO
from mini_framework.authentication.persistent.models import JWTBlacklist
from mini_framework.design_patterns.depend_inject import dataclass_inject
from mini_framework.utils.log import logger


@dataclass_inject
class JWTRules(object):
    jwt_dao: JwtDAO

    async def verify(self, token: str):
        """
        验证token是否已销毁
        :param token:
        :return:
        """
        try:
            from mini_framework.cache.manager import redis_client_manager
            black_token: JWTBlacklist = redis_client_manager.get_client("jwt_blacklist").get(token)
        except Exception as e:
            logger.exception(str(e), exc_info=e, stack_info=True, extra=dict(token=token))
            black_token = await self.jwt_dao.get_token(token)

        return black_token is not None

    async def destroy(self, token, expire_at):
        """
        销毁token
        :param token:
        :param expire_at:
        :return:
        """
        from mini_framework.cache.manager import redis_client_manager
        redis_client_manager.get_client("jwt_blacklist").set(token, 1)
        await self.jwt_dao.add_token(token, expire_at)
        return
