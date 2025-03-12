import os

import jwt
from cryptography import x509
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import serialization

from ..authentication.config import authentication_config
from ..context import env
from ..design_patterns.singleton import singleton
from ..utils.log import logger


@singleton
class JWTUtils:
    def __init__(self):
        self.jwt_config = authentication_config.jwt
        from ..authentication.rules.jwt_rule import JWTRules
        from ..design_patterns.depend_inject import get_injector

        self.jwt_rules: JWTRules = get_injector(JWTRules)
        self.__cert_file = os.path.join(env.app_root, "cert", "token_jwt_key.key")
        self.__certification = None

    @property
    def certification(self):
        if self.__certification is None:
            with open(self.__cert_file, "rb") as f:
                self.__certification = f.read()
        return self.__certification

    def issue(self, payload: dict, tenant=None) -> str:
        """
        生成 JWT
        :param tenant: 租户
        :param payload: 载荷---
        :return: JWT
        """
        payload = payload.copy()
        # 租户的秘钥优先
        if tenant:
            audience = tenant.client_id
            # print('使用租户秘钥',iss  )

        else:
            audience = self.jwt_config.audience
            # print('使用默认配找的iss',iss  )

        payload.update(dict(aud=audience, iss="https://org-center.f123.pub"))
        return jwt.encode(
            payload, self.jwt_config.secret, algorithm=self.jwt_config.algorithm
        )

    async def verify(
        self, token: str, client_id: str = None, cert=None, **kwargs
    ) -> dict:
        """
        验证 JWT
        :param token: JWT
        :param client_id: 客户端 ID
        :param cert: 证书内容
        :return: 载荷
        """
        if client_id is None:
            client_id = self.jwt_config.audience
        if cert is None:
            cert = self.certification
        certificate = x509.load_pem_x509_certificate(cert, default_backend())
        public_bytes = certificate.public_key().public_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PublicFormat.SubjectPublicKeyInfo,
        )
        jwt_payload = jwt.decode(
            token,
            key=public_bytes,
            algorithms=self.jwt_config.algorithm,
            audience=client_id,
            **kwargs
        )
        verified = await self.jwt_rules.verify(token)
        if verified:
            logger.error("Token has been revoked")
            raise jwt.InvalidTokenError("Token has been revoked")
        return jwt_payload

    async def refresh(self, token: str, cert=None) -> str:
        """
        刷新 JWT
        :param token: JWT
        :param cert: 证书内容
        :return: JWT
        """
        if cert is None:
            cert = self.certification
        payload = await self.verify(token, self.jwt_config.audience, cert)
        return self.issue(payload)

    def get_payload(self, token: str) -> dict:
        """
        获取 JWT 载荷
        :param token: JWT
        :return: 载荷
        """
        return jwt.decode(token, options={"verify_signature": False})

    async def destroy(self, token: str):
        """
        销毁 JWT
        :param token: JWT
        """
        payload = self.get_payload(token)
        await self.jwt_rules.destroy(token, payload["exp"])


jwt_utils = JWTUtils()
