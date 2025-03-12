from sqlalchemy import select, update

from mini_framework.authentication.persistent.models import AuthAccount
# from mini_framework.authentication.oauth2 import
from mini_framework.databases.entities.dao_base import DAOBase


class AuthDAO(DAOBase):
    async def get_account_by_id(self, account_id):
        """
        根据账号ID获取账号信息
        """
        session = await self.slave_db()
        result = await session.execute(select(AuthAccount).filter(AuthAccount.account_id == account_id))
        account = result.first()
        return account[0] if account else None

    async def add_account(self, account_id, payload):
        """
        新增账号
        """
        session = await self.master_db()
        account = AuthAccount(account_id=account_id, payload=payload)
        session.add(account)
        return account

    async def update_account(self, account_id, account_dict):
        session = await self.master_db()
        await session.execute(
            update(AuthAccount).filter(AuthAccount.account_id == account_id).values(payload=account_dict)
        )
