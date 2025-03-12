from mini_framework.authentication.config import authentication_config
from mini_framework.authentication.persistent.auth_dao import AuthDAO
from mini_framework.design_patterns.depend_inject import dataclass_inject
from mini_framework.utils.json import JsonUtils
from mini_framework.utils.log import logger
from mini_framework.web.std_models.account import AccountInfo


@dataclass_inject
class AuthRules(object):
    auth_dao: AuthDAO

    async def save_account(self, account_info: AccountInfo, account_dict: dict):
        """
        保存账户信息
        :param account_dict:
        :param account_info:
        """
        try:
            from mini_framework.cache.manager import redis_client_manager

            client = redis_client_manager.get_client("account")
            account_dict_str = JsonUtils.dict_to_json_str(account_dict)
            client.set(
                account_info.account_id,
                account_dict_str,
                ex=authentication_config.jwt.expires + 60,
            )
        except Exception as e:
            logger.exception(
                str(e),
                exc_info=e,
                stack_info=True,
                extra=dict(account_info=account_info),
            )
        exists_account = await self.auth_dao.get_account_by_id(account_info.account_id)
        if not exists_account:
            await self.auth_dao.add_account(account_info.account_id, account_dict)
            return
        exists_account_dict = exists_account.payload
        exists_account_hash = JsonUtils.generate_sha256_signature(exists_account_dict)
        account_hash = JsonUtils.generate_sha256_signature(account_dict)
        if exists_account_hash == account_hash:
            return
        await self.auth_dao.update_account(account_info.account_id, account_dict)

    async def get_account_by_id(self, account_id: str):
        """
        查询账户信息
        :param account_id:
        :return:
        """
        from mini_framework.cache.manager import redis_client_manager

        client = redis_client_manager.get_client("account")
        account_info_str = client.get(account_id)
        if account_info_str:
            account_info = AccountInfo.model_validate_json(account_info_str)
            return account_info
        account_info_db = await self.auth_dao.get_account_by_id(account_id)
        if not account_info_db:
            return None
        account_info = AccountInfo.model_validate_json(account_info_db.payload)
        return account_info
