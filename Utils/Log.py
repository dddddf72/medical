import inspect
import logging
import os.path
import time

from Config.Config import config, PATH_CONFIG, PATH_MODIFY
from Utils.Path import rootPath, storagePath

# 日志文件夹地址
logDirPath = storagePath + "/log"
# 日志文件限量
LOG_FILE_LIMIT = 10


def get_log():
    """
    只能使用 info 函数
    :return: log
    """
    # 日志文件夹整理
    if not os.path.exists(logDirPath):
        # 不存在，新建
        os.mkdir(logDirPath)
    # 获取日志文件夹中所有文件的名字
    fileList = os.listdir(logDirPath)
    # 文件超量，需要清理
    if len(fileList) > LOG_FILE_LIMIT:
        os.remove(logDirPath + "/" + min(fileList))

    # 模式
    if config.log_is_debug:
        logging.basicConfig(level=logging.INFO)
        return logging.getLogger()
    else:
        filename = logDirPath + '/%s.log' % time.strftime('%Y_%m_%d_%H_%M_%S', time.localtime(time.time()))
        logging.basicConfig(level=logging.INFO, filename=filename, filemode='w')
        return logging.getLogger()


__log = get_log()


def log(title, msg=None):
    # 调用者信息
    caller = inspect.stack()[1]
    now_time = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(time.time())) + " timeStamp=" + str(time.time())
    caller_info = " %s - %s[%s] " % (now_time, caller.filename, caller.lineno)

    # 日志完整信息
    log_msg = caller_info + str(title)
    if msg is not None:
        log_msg = log_msg + ": " + str(msg)

    # 打印
    __log.info(log_msg)
    if config.log_print:
        print(log_msg)


# 打印基础配置信息
# 在此打印是为了避免循环引用
log("产品序列号，sn", config.serial_number)
log("项目运行根目录", rootPath)
log("存储目录", storagePath)
log("config", PATH_CONFIG)
log("modify", PATH_MODIFY)
log("log path", logDirPath)
