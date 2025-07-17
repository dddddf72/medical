import configparser
import os.path
import shutil

from Utils.Path import rootPath, storagePath

# 固件版本
FIRMWARE = "Ver 1.0"
# 软件版本
SOFTWARE = "V1.2.1.20210704α"

# 版本
EDITION_DEBUG = "debug"
EDITION_RELEASE = "release"

# 字段为空的特殊字符
EMPTY = "empty"

# 文件路径
# 原始配置
PATH_ORIGINAL = rootPath + "/Config/config.ini"
# 出厂配置
PATH_CONFIG = storagePath + "/Config/config.ini"
# 修改后的配置文件
PATH_MODIFY = storagePath + "/Config/modify.ini"

# 存储目录下不存在配置文件夹
# 需要创建一份，如果是单独测试某页面且页面内需要Config.py时
# 因为存储目录不是根目录会导致新建一份配置文件在测试目录，如同log日志，可直接删除
if not os.path.exists(storagePath + "/Config"):
    os.makedirs(storagePath + "/Config")


class Config(object):
    """
    配置文件管理
    单例模式
    """
    def __init__(self):
        # log 未加载前无法使用 log 打印日志，暂存于此，由 Log 输出
        self.errMsg = ""

        if PATH_ORIGINAL != PATH_CONFIG:
            # 相同目录 ORIGINAL 必然存在，无需操作，避免开发环境修改
            # 不同目录才需要修改
            if not os.path.exists(PATH_CONFIG):
                self.errMsg += "\n 出厂配置文件不存在，复制原始文件"
                # 出厂配置文件不存在，复制一份原始文件为出厂配置文件
                shutil.copyfile(PATH_ORIGINAL, PATH_CONFIG)
            else:
                # 补充
                self.replenish_config(PATH_ORIGINAL, PATH_CONFIG)

        if not os.path.exists(PATH_MODIFY):
            self.errMsg += "\n 修改后配置文件不存在，复制出厂文件"
            # 修改后的配置文件不存在，复制一份出厂配置文件
            shutil.copyfile(PATH_CONFIG, PATH_MODIFY)
        else:
            # 补充
            self.replenish_config(PATH_CONFIG, PATH_MODIFY)

        # 读取配置文件
        self.config = configparser.ConfigParser()
        self.config.read(PATH_MODIFY, encoding='utf-8')

        # 扩展函数
        for section in self.config.sections():
            for key, value in self.config[section].items():
                # 为每个参数扩展set方法 函数名：set_参数名
                self.__dict__["set_%s" % key] = lambda v, s=section, k=key: self.set_value(s, k, v)
                # 为每个参数扩展属性，属性名：参数名
                self.__dict__["%s" % key] = self.get_value(section, key)

    def replenish_config(self, from_path, to_path):
        """
        补充配置项，将from目录下的新增配置添加到to目录下的配置中，不影响两者的其他配置
        :param from_path: 来源配置路径，在总配置项数目中应该较多
        :param to_path: 去向配置路径，可能做了修改的配置，需要保存此修改
        """
        # 读取来源配置文件，调用本函数需确保来源配置是存在且能正常打开的
        fromConfig = configparser.ConfigParser()
        fromConfig.read(from_path, encoding='utf-8')
        # 读取去向配置文件
        try:
            toConfig = configparser.ConfigParser()
            toConfig.read(to_path, encoding='utf-8')

        except BaseException as error:
            self.errMsg += "\n %s 文件损坏打开失败，使用 %s 替代 \n %s" % (to_path, from_path, str(error))
            shutil.copyfile(from_path, to_path)
            return

        # 遍历 section
        for section in toConfig.sections():
            # 遍历配置
            for key, value in toConfig[section].items():
                # 将修改过的配置文件中的配置项保存
                fromConfig.set(section, key, str(value))
        # 保存
        file = open(to_path, 'w')
        fromConfig.write(file)
        file.flush()
        file.close()

    def set_value(self, node, key, value):
        """
        设置配置值
        同时更新缓存值 和 持久化存储

        本函数不做值的合法性判断，此配置主要提供给工程技术人员使用
        无需过度管理，部分数据的限制通过界面 或 调用前的检查进行控制

        :param node: 节点，使用本文件定义的常量
        :param key: 键，使用本文件定义的常量
        :param value: 值
        """
        from Utils.Log import log
        log("set_value [%s].%s" % (node, key), value)
        # 缓存修改
        self.config.set(node, key, str(value))
        self.__dict__["%s" % key] = value
        # 持久化修改
        file = open(PATH_MODIFY, 'w')
        self.config.write(file)
        file.flush()
        file.close()

    def get_value(self, node, key):
        """
        获取配置值
        :param node: 节点，使用本文件定义的常量
        :param key: 键，使用本文件定义的常量
        :return: 配置值
        """
        value = self.config[node][key]
        # 空转换
        if value == EMPTY:
            return None

        # bool 转换
        if value == "True":
            return True
        if value == "False":
            return False

        # int 类型
        try:
            number = int(value)
            return number
        except:
            pass

        # float 类型
        try:
            number = float(value)
            return number
        except:
            # 非数值直接返回
            return value

    @property
    def view_is_debug(self):
        """
        view层是否为debug包
        :return: 是为TRUE
        """
        return self.view == EDITION_DEBUG

    @property
    def model_is_debug(self):
        """
        model层是否为debug包
        :return: 是为TRUE
        """
        return self.model == EDITION_DEBUG

    @property
    def log_is_debug(self):
        """
        日志是否为debug模式
        :return: 是为True
        """
        return self.log == EDITION_DEBUG

    def solidify_config(self):
        """
        固化配置
        将 modify.ini 覆盖到 config.ini 实现配置的固化
        """
        shutil.copyfile(PATH_MODIFY, PATH_CONFIG)


# 单例，import此属性
config = Config()

# 避免循环应用，打印错误日志
from Utils.Log import log
if len(config.errMsg) > 0:
    log("error config", config.errMsg)
