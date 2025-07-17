from Config.Config import config
from Drive.DriveManager import driveManager
from Language.language import string_dict, operate_dict
from Utils.DeviceUtil import shut
from Utils.Log import log
from View.BaseView import main_thread
from View.abstract.CollectView import CollectViewAbstract
from View.custom_widget.MsgBoxDialog import MsgBoxDialog
from View.custom_widget.SettingsDialog import SettingsDialog
from View.release.ReleaseBaseView import ReleaseBaseView
from View.release.collect import collect

# 总格子数
TOTAL_CELL = 100
# 进度条能显示的正常值最大倍数
MULTIPLE_MAX = config.multiple_max
# 出现红色时的倍数
MULTIPLE_RED = config.multiple_red

# 基准值的格子数
# 每格代表值是相等且固定的
# 基准值格子数为REFERENT_CELL，能显示的最大值对应的格子数为 TOTAL_CELL = MULTIPLE_MAX * REFERENT_CELL
REFERENT_CELL = TOTAL_CELL / MULTIPLE_MAX


class CollectView(CollectViewAbstract, collect.Ui_MainWindow, ReleaseBaseView):
    def __init__(self, presenter, referent_value):
        # 正常值
        self.__normalValue = referent_value * presenter.multiple_threshold
        # 正常值格子数
        self.__normalCell = REFERENT_CELL * presenter.multiple_threshold
        # 警告值大小是包含正常值的，所以其格子数需要减去正常值的格子数
        self.set_steps(self.__normalCell, REFERENT_CELL * MULTIPLE_RED - self.__normalCell)

        # 每格大小
        self.__unit = self.__normalValue / self.__normalCell
        # 最大值
        self.__maxValue = TOTAL_CELL * self.__unit
        # 数据
        log("基准值", referent_value)
        log("正常值，阈值", self.__normalValue)
        log("最大值", self.__maxValue)
        log("每格大小", self.__unit)
        log("基准值格子数", REFERENT_CELL)

        # 连台手术的提示
        self.continueDialog = None

        super().__init__(presenter, referent_value)

    def _init_ui(self):
        # 设置正常值
        self.setReferentValue(self._value_to_text(self._referentValue))
        # 连台手术按钮信号
        self.continueButton.clicked.connect(self.__continue_btn_click)
        # 初始化音量
        self.slider.setValue(int(config.volume * 100))
        # 音量改变的信号
        self.slider.sliderReleased.connect(self.__volume_change)
        self.slider.valueChanged.connect(self.__volume_change)
        # 关机
        self.button_shut.clicked.connect(self.__shut)
        # 帮助
        self.button_help.clicked.connect(self.__help)
        # 后门使能
        self.back_door_enable()

    @main_thread
    def refresh_value(self, value):
        # 更新当前值
        self.setCurrentValue(self._value_to_text(value))
        # 更新进度条
        self.equalizer.setValues(self.__referent_map(value))
        # 更新倍数值，暂用测量值的方法，当前倍数值获取可看作测量值的子集
        self.setMultipleValue(self._value_to_text(value / self._referentValue))

    @main_thread
    def close_dialog(self):
        if self.continueDialog is not None:
            self.continueDialog.close()

    def __referent_map(self, value):
        """
        将数值映射到 [0,100]
        :param value: 荧光值
        :return: [0,100]
        """
        value = abs(value)
        # 大于最大值，按最大值处理
        if value >= self.__maxValue:
            return TOTAL_CELL

        # 其他情形的格子数
        return value / self.__unit

    def __continue_btn_click(self):
        """
        点击连台手术按钮
        """
        log("__continue_btn_click")
        # 弹框确认
        self.continueDialog = MsgBoxDialog(
            operate_dict("continueOperation"),
            string_dict("continueOperationConfirm"),
            operate_dict("installSheathFinish"), self.presenter.install_complete,
            operate_dict("cancel"), None
        )
        self.continueDialog.show()
        # 注册手柄模式键双击回调事件
        driveManager.register_mode_double_click_callback(self.presenter.install_complete_mode_click)

    def __volume_change(self, volume=-1):
        """
        音量改变时
        :param volume 音量[0,100]
        """
        # 还在按着，不做修改
        if self.slider.isSliderDown():
            return
        # 修改
        volume = self.slider.value()
        self.presenter.set_volume(volume / 100)

    def __shut(self):
        """
        关机
        """
        # 弹框提示
        self.shutDialog = MsgBoxDialog(
            string_dict("shutTip"),
            string_dict("shutMsg"),
            operate_dict("shut"), shut,
            operate_dict("cancel"), None
        )
        self.shutDialog.show()

    def __help(self):
        """
        帮助
        """
        self.settingsDialog = SettingsDialog()
        self.settingsDialog.show()
