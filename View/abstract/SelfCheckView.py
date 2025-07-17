import abc

import numpy as np
from PyQt5 import QtCore
from numpy import array

from Language.language import string_dict
from Utils.Log import log
from Utils.Path import rootPath
from View.BaseView import BaseView

# 图片所在路径
imgPath = rootPath + "/View/img/selfcheck"

# 各模块对应各状态的二维数组
MODULE_STATUS_ARRAY = np.array([
    # 激光模块
    [
        imgPath + "/待自检_41",
        imgPath + "/自检中_09",
        imgPath + "/自检通过_07",
        imgPath + "/自检异常_43"
    ],
    # 光开关模块
    [
        imgPath + "/待自检_50",
        imgPath + "/自检中_25",
        imgPath + "/自检通过_24",
        imgPath + "/自检异常_51"
    ],
    # apd模块
    [
        imgPath + "/待自检_55",
        imgPath + "/自检中_30",
        imgPath + "/自检通过_29",
        imgPath + "/自检异常_56"
    ],
    # 光纤模块
    [
        imgPath + "/待自检_59",
        imgPath + "/自检中_38",
        imgPath + "/自检通过_37",
        imgPath + "/自检异常_60"
    ]
])
# 状态图标数组
STATUS_ARRAY = np.array([
    imgPath + "/自检状态_03-12.png",
    imgPath + "/自检动画.gif",
    imgPath + "/自检状态_05-15.png",
    imgPath + "/自检状态_09-31.png"
])
# 详细模块自检异常时的错误提示。本数组不能与模块索引一起使用，因为本数组包含更详细的模块信息。
DETAILED_MODULE_ERROR_ARRAY = np.array([
    string_dict("laserDeviceError"),
    string_dict("lightSwitchError"),
    string_dict("apdError"),
    string_dict("niError"),
    string_dict("fibreOpticalError")
])
# 需要检查的模块在数组中的索引。这里所说的模块是大模块，不包含细节模块，对应展现给用户观看的模块
MODULE_LASER = 0
MODULE_LIGHT_SWITCH = 1
MODULE_APD = 2
MODULE_FIBRE_OPTICAL = 3
# 自检状态在数组中的索引
STATUS_WAIT = 0
STATUS_RUNNING = 1
STATUS_SUCCESS = 2
STATUS_ERROR = 3
# 模块日志数组，用于日志输出
MODULE_LOG_ARRAY = np.array([
    "激光模块",
    "光开关模块",
    "传感器模块",
    "光纤模块"
])
# 状态日志日志数组，用于日志输出
STATUS_LOG_ARRAY = np.array([
    "等待检查",
    "正在检查",
    "模块正常",
    "模块异常"
])


class SelfCheckViewAbstract(BaseView):
    """
    自检界面
    """
    # 信号
    boot_check_success_signal = QtCore.pyqtSignal()
    mode_open_check_success_signal = QtCore.pyqtSignal()
    update_module_status_signal = QtCore.pyqtSignal(int, int)
    update_module_signal = QtCore.pyqtSignal(int)
    close_dialog_signal = QtCore.pyqtSignal()

    def __init__(self, presenter):
        super().__init__(presenter)
        # 信号绑定
        self.boot_check_success_signal.connect(self.boot_check_success)
        self.mode_open_check_success_signal.connect(self.mode_open_check_success)
        self.update_module_status_signal.connect(self.update_module_status)
        self.update_module_signal.connect(self.update_module)
        self.close_dialog_signal.connect(self.close_dialog)

    @abc.abstractmethod
    def boot_check_success(self):
        """
        开机自检正常
        """
        pass

    @abc.abstractmethod
    def mode_open_check_success(self):
        """
        模式键打开的自检成功
        """
        pass

    @abc.abstractmethod
    def check_error(self, detailed_module_status_list: array) -> str:
        """
        自检发现异常
        :param detailed_module_status_list: 详细模块状态数组
        :return: 异常简要信息
        """
        log("check_error detailed_module_status_list", detailed_module_status_list)
        error = ""
        for index, value in enumerate(detailed_module_status_list):
            # False 时为异常需要详情
            error += DETAILED_MODULE_ERROR_ARRAY[index] + "\n" if not value else ""

        log("check_error", error)
        return error

    @abc.abstractmethod
    def update_module_status(self, module, status):
        """
        更新模块状态

        参数使用本文件的常量
        :param module: 模块
        :param status: 状态
        """
        log("update_module_status", "%s, %s" % (MODULE_LOG_ARRAY[module], STATUS_LOG_ARRAY[status]))

    @abc.abstractmethod
    def update_module(self, module):
        """
        更新模块进度
        需要是耗时操作
        :param module: 当前模块
        """
        pass

    @abc.abstractmethod
    def close_dialog(self):
        """
        关闭所有dialog
        """
        pass
