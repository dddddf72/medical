import abc

from PyQt5 import QtCore
from PyQt5.QtCore import QTimer

from Utils.Log import log
from View.BaseView import BaseView, main_thread

# 预热进度最大值
PROGRESS_MAX = 100


class MainViewAbstract(BaseView):
    """
    主界面实现
    """
    # 信号
    laser_power_check_progress_signal = QtCore.pyqtSignal(int, int, int, int)
    laser_power_stable_signal = QtCore.pyqtSignal()
    laser_power_instability_signal = QtCore.pyqtSignal()
    open_self_check_signal = QtCore.pyqtSignal(bool)
    init_drive_error_signal = QtCore.pyqtSignal(str)
    start_preheat_signal = QtCore.pyqtSignal(int)
    preheat_progress_signal = QtCore.pyqtSignal()

    def __init__(self, presenter):
        super().__init__(presenter)
        # 信号绑定
        self.laser_power_check_progress_signal.connect(self.laser_power_check_progress)
        self.laser_power_stable_signal.connect(self.laser_power_stable)
        self.laser_power_instability_signal.connect(self.laser_power_instability)
        self.open_self_check_signal.connect(self.open_self_check)
        self.init_drive_error_signal.connect(self.init_drive_error)
        self.start_preheat_signal.connect(self.start_preheat)
        self.preheat_progress_signal.connect(self.preheat_progress)

        # 预热定时器
        self._preheatTimer = None

    @main_thread
    def start_preheat(self, time):
        """
        开始预热
        预热结束应该通知 presenter 层
        进度条总长为 100
        :param time: 预热时长，单位：分钟
        """
        # 分钟 转 毫秒 再计算每格进度的时间
        unit = time * 60 * 1000 / PROGRESS_MAX
        log("预热时长：%s分钟，格数：%s，每格：%s毫秒" % (time, PROGRESS_MAX, unit))
        # 初始化进度为1
        self.preheat_progress()
        # 定时器
        self._preheatTimer = QTimer(self)
        self._preheatTimer.timeout.connect(self.preheat_progress)
        self._preheatTimer.start(unit)

    @abc.abstractmethod
    def preheat_progress(self):
        """
        预热进度
        预热结束应该通知 presenter 层
        """
        pass

    @abc.abstractmethod
    def laser_power_check_progress(
            self,
            stable_sum,
            stable_max,
            check_retry_sum,
            check_retry_max
    ):
        """
        激光功率检查进度
        :param stable_sum: 有效稳定次数
        :param stable_max: 稳定最大次数
        :param check_retry_sum: 当前重试次数
        :param check_retry_max: 最大重试次数
        """
        pass

    @abc.abstractmethod
    def laser_power_stable(self):
        """
        激光功率稳定
        """
        pass

    @abc.abstractmethod
    def laser_power_instability(self):
        """
        激光功率不稳定
        """
        pass

    @main_thread
    def open_self_check(self, is_mode_key_open):
        """
        打开自检界面
        :param is_mode_key_open: 是否为通过模式键打开
        """
        self.presenter.open_self_check(is_mode_key_open)

    @abc.abstractmethod
    def init_drive_error(self, msg):
        """
        初始化设备失败的操作
        :param msg: 错误信息
        """
        pass

    @abc.abstractmethod
    def need_confirm_tip(self, msg):
        """
        需要确认的提示
        确认提示后将回调 presenter 的确认提示回调函数
        :param msg: 提示内容
        """
        pass
