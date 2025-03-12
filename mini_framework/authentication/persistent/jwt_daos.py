from sqlalchemy import select

from mini_framework.authentication.persistent.models import JWTBlacklist
from mini_framework.databases.entities.dao_base import DAOBase


class JwtDAO(DAOBase):
    async def get_token(self, token):
        """
        获取token
        :param token:
        :return:
        """
        session = await self.slave_db()
        result = await session.execute(select(JWTBlacklist).filter(JWTBlacklist.jwt_token == token))
        return result.first()

    async def add_token(self, token, expire_at):
        """
        新增token
        :param token:
        :param expire_at:
        :return:
        """
        session = await self.master_db()
        token = JWTBlacklist(jwt_token=token, expire_at=expire_at)
        session.add(token)
        await session.refresh(token)
        return token
