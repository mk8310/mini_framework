import hashlib


class DataSecureUtil:
    """
    需要实现数据安全相关的方法：
    1. 手机号脱敏
    2. 身份证号脱敏
    3. 银行卡号脱敏
    4. 邮箱脱敏
    5. 密码加密
    """

    @staticmethod
    def desensitize_phone(phone: str) -> str:
        """
        手机号脱敏
        :param phone: 手机号
        :return: 脱敏后的手机号
        """
        return phone[:3] + "****" + phone[-4:]

    @staticmethod
    def desensitize_id_card(id_card: str) -> str:
        """
        身份证号脱敏
        :param id_card: 身份证号
        :return: 脱敏后的身份证号
        """
        return id_card[:6] + "********" + id_card[-4:]

    @staticmethod
    def desensitize_bank_card(bank_card: str) -> str:
        """
        银行卡号脱敏
        :param bank_card: 银行卡号
        :return: 脱敏后的银行卡号
        """
        return bank_card[:6] + "****" + bank_card[-4:]

    @staticmethod
    def desensitize_email(email: str) -> str:
        """
        邮箱脱敏
        :param email: 邮箱
        :return: 脱敏后的邮箱
        """
        username, domain = email.split("@")
        return username[:3] + "****" + "@" + domain

    @staticmethod
    def desensitize_address(address: str) -> str:
        """
        地址脱敏
        :param address: 地址
        :return: 脱敏后的地址
        """
        return address[:3] + "****" + address[-4:]

    @staticmethod
    def encrypt_password(password: str) -> str:
        """
        密码加密
        :param password: 密码
        :return: 加密后的密码
        """
        return hashlib.md5(password.encode()).hexdigest()
