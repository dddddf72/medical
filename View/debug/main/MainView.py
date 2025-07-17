import time

from PyQt5.QtCore import QTimer

from Config.Config import config
from Drive.DriveManager import driveManager
from Utils.Log import log
from View.BaseView import main_thread
from View.abstract.MainView import MainViewAbstract, PROGRESS_MAX
from View.config.ConfigView import ConfigView
from View.debug.DebugBaseView import DebugBaseView
from View.debug.main import main


class MainView(MainViewAbstract, main.Ui_MainWindow, DebugBaseView):

    def __init__(self, presenter):
        super().__init__(presenter)
        self.lastTime = time.time()
        # 配置界面
        self.__configView = None
        # 当前预热进度
        self.__preheat_now = 0

    def _refresh_config(self):
        self.viewLineEdit.setReadOnly(True)
        self.viewLineEdit.setText(config.view)
        self.modelLineEdit.setReadOnly(True)
        self.modelLineEdit.setText(config.model)
        self.modelLineEdit.setReadOnly(True)
        self.fluorescenceLineEdit.setText("value")

    @main_thread
    def init_drive_error(self, msg):
        self.error(msg)

    @main_thread
    def start_preheat(self, time):
        self.__preheat_now = 0
        super().start_preheat(time)

    @main_thread
    def preheat_progress(self):
        """
        预热进度
        """
        # 更新当前进度
        self.__preheat_now += 1
        self.logTextBrowser.append("预热进度：%s / 100" % self.__preheat_now)
        # 预热结束
        # 留一格给初始化
        if self.__preheat_now >= PROGRESS_MAX - 1:
            self._preheatTimer.stop()
            self.presenter.preheat_end()

    @main_thread
    def laser_power_check_progress(
            self,
            stable_sum,
            stable_max,
            check_retry_sum,
            check_retry_max
    ):
        self.logTextBrowser.append(
            "稳定次数: %d / %d 重试次数: %d / %d"
            % (stable_sum, stable_max, check_retry_sum, check_retry_max)
        )

    @main_thread
    def laser_power_stable(self):
        self.logTextBrowser.append("激光功率稳定")

    @main_thread
    def laser_power_instability(self):
        self.logTextBrowser.append("激光功率不稳定，请检查硬件重试")

    def _init_ui(self):
        # 信号连接信号槽
        self.powerUpPushButton.clicked.connect(self.power_up_btn_click)
        self.selfCheckPushButton.clicked.connect(self.self_check_btn_click)
        self.getReferencePushButton.clicked.connect(self.referent_btn_click)
        self.checkPushButton.clicked.connect(self.check_btn_click)
        # 检测键信号
        self.readShortPushButton.clicked.connect(self.read_short_click)
        self.readQuickPushButton.clicked.connect(self.read_quick_click)
        self.readPressPushButton.clicked.connect(self.read_press)
        self.readBouncePushButton.clicked.connect(self.read_bounce)
        # 检测键事件
        self.shortRegisterPushButton.clicked.connect(self.short_register)
        self.longRegisterPushButton.clicked.connect(self.long_register)
        self.shortUnboundPushButton.clicked.connect(self.short_unbound)
        self.longUnboundPushButton.clicked.connect(self.long_unbound)
        # 模式键信号
        self.modePressPushButton.clicked.connect(self.mode_press)
        self.modeBouncePushButton.clicked.connect(self.mode_bounce)
        # 配置键
        self.configPushButton.clicked.connect(self.config_btn_click)
        # 确认提示
        self.confirmTipPushButton.clicked.connect(self.confirm_tip)

    def power_up_btn_click(self):
        """
        点击开机按钮
        """
        self.logTextBrowser.append("点击开机按钮")
        log("点击开机按钮")
        self.presenter.power_up_init()

    def self_check_btn_click(self):
        """
        自检按钮点击
        TODO MS 22.1.15 会卡死
        """
        self.logTextBrowser.append("自检按钮点击")
        log("自检按钮点击")
        self.open_self_check(True)

    def check_btn_click(self):
        """
        检测采集按钮点击
        """
        self.logTextBrowser.append("检测采集按钮点击")
        log("检测采集按钮点击")
        self.presenter.open_collect()

    def referent_btn_click(self):
        """
        取基准值按钮点击
        """
        self.logTextBrowser.append("取基准值按钮点击")
        log("取基准值按钮点击")
        self.presenter.open_referent()

    def read_short_click(self):
        """
        检测键按下抬起，大于0.3s抬起
        """
        self.logTextBrowser.append("检测键按下抬起")
        driveManager.read_simulate_btn_press()
        timer = QTimer(self)
        timer.singleShot(400, driveManager.read_simulate_btn_bounce)

    def read_quick_click(self):
        """
        检测键快速按下抬起，小于0.3s
        """
        self.logTextBrowser.append("检测键快速按下抬起")
        driveManager.read_simulate_btn_press()
        timer = QTimer(self)
        timer.singleShot(200, driveManager.read_simulate_btn_bounce)

    def read_press(self):
        """
        检测键长按，不抬起
        """
        self.logTextBrowser.append("检测键按下")
        driveManager.read_simulate_btn_press()

    def read_bounce(self):
        """
        检测键抬起
        """
        self.logTextBrowser.append("检测键抬起")
        driveManager.read_simulate_btn_bounce()

    def short_register(self):
        self.logTextBrowser.append("短按注册")
        driveManager.register_read_short_click_callback(self.fluorescence_callback)

    def long_register(self):
        self.logTextBrowser.append("长按注册")
        driveManager.register_read_long_click_callback(self.fluorescence_callback)

    def short_unbound(self):
        self.logTextBrowser.append("短按解绑")
        driveManager.unbound_read_short_click_callback(self.fluorescence_callback)

    def long_unbound(self):
        self.logTextBrowser.append("长按解绑")
        driveManager.unbound_read_long_click_callback(self.fluorescence_callback)

    def fluorescence_callback(self, data):
        self.fluorescenceLineEdit.setText(str(data))
        # 间隔2s打印一个，避免疯狂刷新
        if time.time() - self.lastTime > 2:
            self.lastTime = time.time()
            self.logTextBrowser.append(str(data))

    def mode_press(self):
        """
        模式键按下
        """
        self.logTextBrowser.append("模式键按下")
        driveManager.mode_simulate_btn_press()

    def mode_bounce(self):
        """
        模式键抬起
        """
        self.logTextBrowser.append("模式键抬起")
        driveManager.mode_simulate_btn_bounce()

    def config_btn_click(self):
        """
        配置键点击
        """
        self.__configView = ConfigView()
        self.__configView.show()

    def need_confirm_tip(self, msg):
        """
        需要确认的提示
        确认提示后将回调 presenter 的确认提示回调函数
        :param msg: 提示内容
        """
        self.logTextBrowser.append(msg)
        self.logTextBrowser.append("请点击确认提示按钮")

    def confirm_tip(self):
        """
        点击确认提示按钮
        """
        self.logTextBrowser.append("点击了确认提示按钮")
        self.presenter.confirm_tip()
