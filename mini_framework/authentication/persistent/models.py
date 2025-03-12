from sqlalchemy import String, JSON
from sqlalchemy.orm import Mapped, mapped_column

from mini_framework.databases.entities import BaseDBModel


class JWTBlacklist(BaseDBModel):
    __tablename__ = "jwt_blacklist"
    __table_args__ = {"comment": "token 黑名单"}

    jwt_token: Mapped[str] = mapped_column(String(2000), primary_key=True, comment="jwt token")
    expire_at: Mapped[int] = mapped_column(comment="过期时间戳")


class AuthAccount(BaseDBModel):
    __tablename__ = "auth_account"
    __table_args__ = {"comment": "账号信息"}

    account_id: Mapped[int] = mapped_column(String(255), primary_key=True, comment="账号ID")
    payload: Mapped[JSON] = mapped_column(JSON, comment="用户信息")
