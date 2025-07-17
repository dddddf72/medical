from PyQt5.QtCore import QTimer

from Language.language import string_dict, operate_dict
from Utils.DeviceUtil import shut, reboot, restart_app
from Utils.Log import log
from View.BaseView import main_thread
from View.abstract.MainView import MainViewAbstract, PROGRESS_MAX
from View.custom_widget.MsgBoxDialog import MsgBoxDialog
from View.release.ReleaseBaseView import ReleaseBaseView
from View.release.main import main


class MainView(MainViewAbstract, main.Ui_MainWindow, ReleaseBaseView):
    def __init__(self, presenter):
        super().__init__(presenter)
        # 预热错误提示
        self.errorDialog = None

    def _init_ui(self):
        # 后门使能
        self.back_door_enable()

    @main_thread
    def init_drive_error(self, msg):
        # 弹框提示
        self.errorDialog = MsgBoxDialog(
            string_dict("tip"),
            msg,
            operate_dict("shut"), shut,
            operate_dict("reboot"), reboot
        )
        self.errorDialog.show()

    @main_thread
    def preheat_progress(self):
        """
        预热进度
        """
        # 更新当前进度
        preheat_now = self.progressBar.value() + 1
        self.update_value(preheat_now, PROGRESS_MAX)
        # 预热结束
        # 留一格给初始化
        if preheat_now >= PROGRESS_MAX - 1:
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
        if stable_sum == stable_max:
            self.update_value(PROGRESS_MAX, PROGRESS_MAX)

    @main_thread
    def laser_power_stable(self):
        self.update_value(100, 100)
        # 隐藏本界面
        hideTimer = QTimer(self)
        hideTimer.singleShot(1000, self.hide)

    @main_thread
    def laser_power_instability(self):
        log("激光不稳定，初始化异常")
        # 弹框提示
        self.errorDialog = MsgBoxDialog(
            string_dict("tip"),
            string_dict("laserPowerError"),
            operate_dict("rebootDevice"), reboot,
            operate_dict("restartApp"), restart_app
        )
        self.errorDialog.show()

    def need_confirm_tip(self, msg):
        """
        需要确认的提示
        确认提示后将回调 presenter 的确认提示回调函数
        :param msg: 提示内容
        """
        self.__needConfirmTipDialog = MsgBoxDialog(
            string_dict("tip"),
            msg,
            None, None,
            operate_dict("confirm"), self.presenter.confirm_tip
        )
        self.__needConfirmTipDialog.show()
