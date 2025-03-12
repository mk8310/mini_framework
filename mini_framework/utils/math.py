def generate_charset(base):
    """
    根据 base 自动生成字符集。
    支持的字符包括数字、大写字母、小写字母，共计 62 个字符。
    """
    all_chars = '0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz'
    if base > len(all_chars):
        raise ValueError(f"Base {base} 超过最大支持的进制 (36)")
    return all_chars[:base]

def decimal_to_base(num, base:int)->str:
    """
    将一个十进制数转换为n进制数
    :param num: 待转换的数
    :param base: 进制
    :param precision: 小数部分精度
    :return: 转换后的字符串
    """
    if base < 2:
        raise ValueError("进制必须大于等于2")
    if base > 36:
        raise ValueError("进制必须小于等于36")
    digits = "0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZ"
    if num == 0:
        return "0"
    negative = num < 0
    num = abs(num)
    result = ""
    while num > 0:
        result = digits[num % base] + result
        num = num // base
    if negative:
        result = "-" + result
    return result
