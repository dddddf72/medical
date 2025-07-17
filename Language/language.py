from Language.zh_CN import stringDict, operateDict

# 语言配置
LANGUAGE = "zh_CN"


def string_dict(key):
    """
    获取字符串提示字典
    :return: 字典
    """
    return stringDict[key]


def operate_dict(key):
    """
    获取字符串操作字典
    :return: 字典
    """
    return operateDict[key]
