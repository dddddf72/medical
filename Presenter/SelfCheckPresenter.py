from PyQt5.QtCore import QTimer

from Config.Config import *
from Drive.DriveManager import driveManager
from Model.Factory import SelfCheckModelFactory
from Presenter.BasePresenter import BasePresenter
from Presenter.ReferentPresenter import ReferentPresenter
from Utils.Log import log
from View.Factory import SelfCheckViewFactory
from View.abstract.SelfCheckView import *

# 仿体预设荧光值
PRESET_IMITATION_FLUORESCENCE = config.preset_imitation_fluorescence
# 荧光值的最大差值，大于该差值为异常
FLUORESCENCE_DIFFERENCE_MAX = config.fluorescence_difference_max


class SelfCheckPresenter(BasePresenter):
    def __init__(self):
        # V M 层
        super().__init__()
        self.__selfCheckModel = SelfCheckModelFactory.get_instance(self)
        self.__selfCheckView = SelfCheckViewFactory.get_instance(self)
        # 仿体预设值，若为模式键打开需要通过RFID更新
        self.__imitationValue = PRESET_IMITATION_FLUORESCENCE
        # 是否为模式键打开的本界面
        self.__isModeKeyOpen = False
        # 持有被打开的取基准值界面，避免被回收
        self.__referentPresenter = None
        # 模块检查的迭代器
        self.__module_check_generator = None
        # 自检结果，None：还没通过（若已经回调，即认为异常）；False：状态异常；True：状态正常
        self.__laserStatus = None
        self.__lightSwitchStatus = None
        self.__apdStatus = None
        self.__niStatus = None
        self.__fibreOpticalStatus = None

        # 灯闪烁线程
        self.__lampReverseTimer = QTimer(self, timeout=self.__selfCheckModel.lamp_reverse)

    @property
    def _view(self):
        return self.__selfCheckView

    def show(self, is_mode_key_open=False):
        super(SelfCheckPresenter, self).show()
        self.__isModeKeyOpen = is_mode_key_open
        # 注册手柄短按事件，即使没有使用按键，也将使用短按事件的回调
        driveManager.register_read_short_click_callback(self.fluorescence_value)
        # 注册光开关回调
        driveManager.register_light_switch_callback(self.__selfCheckView.light_switch_callback)
        # 手柄灯闪烁
        self.__lampReverseTimer.start(200)

        # 显示
        self.__selfCheckView.show()
        # 开始快速自检
        self.boot_check()

    def _close(self):
        super(SelfCheckPresenter, self)._close()
        # 停止手柄闪烁控制
        self.__lampReverseTimer.stop()
        # 取绑回调事件
        driveManager.unbound_read_short_click_callback(self.fluorescence_value)
        driveManager.unbound_mode_double_click_callback(self.install_complete_mode_click)
        driveManager.unbound_light_switch_callback(self.__selfCheckView.light_switch_callback)
        # 回收
        self.__selfCheckModel = None
        self.__selfCheckView.close()
        self.__selfCheckView = None

    def boot_check(self):
        """
        开机自检
        获取荧光值，再进入快速自检
        获取到荧光值的回调： fluorescence_value
        """
        # 获取荧光值
        driveManager.read_short_click_thread()

    def fluorescence_value(self, value):
        """
        读取到荧光值
        将进入快速自检流程
        :param value: 荧光值
        """
        self.__quick_check(self.__imitationValue, value)

    def __quick_check(self, imitation, read_value):
        """
        快速自检，已经获取
        :param imitation: 仿体荧光值
        :param read_value: 探头读取到的值
        """
        # 判断差距
        deviceStatus = True
        if abs(imitation - read_value) < FLUORESCENCE_DIFFERENCE_MAX:
            log("quick_check", "设备正常")
            deviceStatus = True
        else:
            # 设备异常
            log("quick_check error", "设备异常")
            log("fluorescence error", read_value)
            deviceStatus = False
        # 模块检查
        self.__module_check_generator = self.__module_check(deviceStatus)
        # 启动迭代器
        self.module_check()

    def module_check(self):
        """
        模块检查对外接口，迭代器管理
        """
        try:
            log("module_check", "next")
            next(self.__module_check_generator)
        except StopIteration:
            log("module_check", "StopIteration")

    def __module_check(self, default_status=True):
        """
        模块检查的流程

        self.__selfCheckView.update_module 将回调 self.presenter.module_check
        此举将引起迭代器 next 操作，所以 update_module 需为耗时操作，因为本逻辑未先yield
        不然将引起迭代器运行中的错误

        模块的实际检查如果是耗时操作应该使用异步处理，避免卡顿界面

        :param default_status:  默认状态，若为True 则所有模块默认正常
                                当快速自检通过时，可设为True，避免重复检查
        :return: 迭代器
        """
        log("__module_check", default_status)
        # 检查激光模块
        self.__laserStatus = default_status or self.__selfCheckModel.laser_device_status()
        self.__selfCheckView.update_module(MODULE_LASER)

        yield
        # 激光状态
        if self.__laserStatus:
            self.__selfCheckView.update_module_status(MODULE_LASER, STATUS_SUCCESS)
        else:
            self.__selfCheckView.update_module_status(MODULE_LASER, STATUS_ERROR)

        # 检查光开关模块
        self.__lightSwitchStatus = default_status or self.__selfCheckModel.light_switch_status()
        self.__selfCheckView.update_module(MODULE_LIGHT_SWITCH)

        yield
        # 光开关状态
        if self.__lightSwitchStatus:
            self.__selfCheckView.update_module_status(MODULE_LIGHT_SWITCH, STATUS_SUCCESS)
        else:
            self.__selfCheckView.update_module_status(MODULE_LIGHT_SWITCH, STATUS_ERROR)

        # 数据采集卡模块
        self.__niStatus = default_status or self.__selfCheckModel.ni_status()
        # 检查APD模块
        self.__apdStatus = default_status or self.__selfCheckModel.apd_status()
        self.__selfCheckView.update_module(MODULE_APD)

        yield
        # 传感器状态
        if self.__apdStatus and self.__niStatus:
            self.__selfCheckView.update_module_status(MODULE_APD, STATUS_SUCCESS)
        else:
            self.__selfCheckView.update_module_status(MODULE_APD, STATUS_ERROR)

        # 存在异常状态。此时不再进行光纤自检动画
        if not self.electric_module_normal():
            # 详情提示
            self.__check_error()
            yield

        # 启动光纤检查的动画，光纤实际不需要检查
        # default_status = True: 光纤正常
        # default_status = False: 所有模块正常时，光纤判定异常；有一个模块异常时，光纤判定正常
        self.__fibreOpticalStatus = default_status or (not self.electric_module_normal())
        self.__selfCheckView.update_module(MODULE_FIBRE_OPTICAL)

        yield
        if not self.__fibreOpticalStatus:
            # 光纤异常
            self.__selfCheckView.update_module_status(MODULE_FIBRE_OPTICAL, STATUS_ERROR)
            # 详情提示
            self.__check_error()
            yield

        # 一切正常
        self.__selfCheckView.update_module_status(MODULE_FIBRE_OPTICAL, STATUS_SUCCESS)
        self.__selfCheckView.boot_check_success()

    def install_complete(self):
        """
        无菌护套装配完成
        进入取基准值界面
        该由UI线程调用
        """
        # 延时关闭自检界面
        QTimer(self).singleShot(1000, self._close)
        # 打开取基准值界面
        self.__referentPresenter = ReferentPresenter()
        self.__referentPresenter.show()

    def get_self_check_model_test(self):
        """
        获取自检model层
        仅限测试时使用，不得在生产中使用
        :return: self_check_model
        """
        return self.__selfCheckModel

    def get_is_mode_key_open(self):
        return self.__isModeKeyOpen

    def electric_module_normal(self) -> bool:
        """
        电子模块正常
        不包含光纤的其他所有模块
        :return: 正常返回：True；存在异常 或 未知：False
        """
        laserStatus = False if self.__laserStatus is None else self.__laserStatus
        lightSwitchStatus = False if self.__lightSwitchStatus is None else self.__lightSwitchStatus
        apdStatus = False if self.__apdStatus is None else self.__apdStatus
        niStatus = False if self.__niStatus is None else self.__niStatus
        return laserStatus and lightSwitchStatus and apdStatus and niStatus

    def __check_error(self):
        """
        自检异常
        光纤模块状态由电子模块辅助判定
        """
        # 本数组含义；长度；顺序，应当与 View.abstract.SelfCheckView.DETAILED_MODULE_ERROR_ARRAY 保持一致
        self.__selfCheckView.check_error([
            self.__laserStatus,
            self.__lightSwitchStatus,
            self.__apdStatus,
            self.__niStatus,
            not self.electric_module_normal()
        ])

    def install_complete_mode_click(self):
        """
        通过模式键点击实现装配完成的确定
        """
        log("install_complete_mode_click")
        # 仅允许回调一次
        driveManager.unbound_mode_double_click_callback(self.install_complete_mode_click)
        # 关闭dialog
        self.__selfCheckView.close_dialog()
        # 装配完成
        self.install_complete()

    def _mode_long_click(self):
        """
        重写 模式键长按
        本界面模式键长按功能未启用，需要屏蔽掉底层注册
        """
        pass
