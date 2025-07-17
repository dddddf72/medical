from PyQt5.QtCore import QTimer
from PyQt5.QtGui import QPixmap, QMovie

from Drive.DriveManager import driveManager
from Language.language import operate_dict
from Utils.DeviceUtil import shut, reboot
from Utils.Log import log
from Utils.ResolutionTools import scaleSizeW, scaleSizeH
from View.BaseView import main_thread
from View.abstract.SelfCheckView import *
from View.custom_widget.MsgBoxDialog import MsgBoxDialog
from View.release.ReleaseBaseView import ReleaseBaseView
from View.release.self_check import self_check

# 模块进度时间间隔，单位：毫秒
MODULE_INTERVAL = 10
# 总体进度时间间隔，单位：毫秒
TOTAL_INTERVAL = 30


class SelfCheckView(SelfCheckViewAbstract, self_check.Ui_MainWindow, ReleaseBaseView):
    # 模块动画结束的信号
    module_animation_finish_signal = QtCore.pyqtSignal()

    def __init__(self, presenter):
        super().__init__(presenter)
        # 信号绑定
        self.module_animation_finish_signal.connect(self.presenter.module_check)
        # 定时器初始化
        self.__moduleTimer = QTimer(self)
        self.__moduleTimer.timeout.connect(self.__update_module)
        self.__totalTimer = QTimer(self)
        self.__totalTimer.timeout.connect(self.__update_total)
        # 整体进度目标值
        self.__totalTarget = 0
        # 当前模块
        self.__currentModule = None
        # 安装护套的提示
        self.installDialog = None

    def _init_ui(self):
        # 后门使能
        self.back_door_enable()
        # 模块控件
        self.__moduleViewList = [
            self.label,
            self.label_2,
            self.label_3,
            self.label_4
        ]
        # 状态控件
        self.__statusViewList = [
            self.label_6,
            self.label_7,
            self.label_8,
            self.label_9
        ]

    @main_thread
    def error(self, msg):
        super(SelfCheckView, self).error(msg)
        self.show_tip(msg)

    @main_thread
    def tip(self, msg):
        super(SelfCheckView, self).tip(msg)
        self.show_tip(msg)

    def __rfid_btn_click(self):
        """
        点击RFID读取按钮
        """
        log("读取仿体内置荧光值")

    def __read_btn_click(self):
        """
        点击探头取值按钮
        """
        log("探头取值")

    def __install_btn_click(self):
        """
        点击装备完成按钮
        """
        log("装备完成")
        self.presenter.install_complete()

    @main_thread
    def boot_check_success(self):
        log("boot_check_success", "自检正常")
        self.installDialog = MsgBoxDialog(
            string_dict("tip"),
            string_dict("installSheath"),
            None, None,
            operate_dict("installSheathFinish"), self.presenter.install_complete
        )
        self.installDialog.show()

        # 取绑短按读值，避免重复自检
        driveManager.unbound_read_short_click_callback(self.presenter.fluorescence_value)
        # 使能手柄按键，让模式键控制生效
        driveManager.set_button_enable(True)
        # 注册手柄模式键双击回调事件
        driveManager.register_mode_double_click_callback(self.presenter.install_complete_mode_click)

    @main_thread
    def mode_open_check_success(self):
        log("mode_open_check_success", "自检正常")

    @main_thread
    def check_error(self, detailed_module_status_list: array):
        error = super(SelfCheckView, self).check_error(detailed_module_status_list)
        # 简要提示
        self.error(error)
        # 弹框提示
        self.errorDialog = MsgBoxDialog(
            string_dict("tip"),
            string_dict("selfCheckError"),
            operate_dict("shut"), shut,
            operate_dict("reboot"), reboot
        )
        self.errorDialog.show()

    @main_thread
    def update_module_status(self, module, status):
        """
        更新模块状态
        参数必须使用 abstract/SelfCheckView 文件定义的值
        :param module: 模块索引
        :param status: 状态索引
        """
        super(SelfCheckView, self).update_module_status(module, status)
        # 自检中，使用gif
        gif = None
        if status == STATUS_RUNNING:
            gif = QMovie(STATUS_ARRAY[status])

        # 模块状态
        self.__moduleViewList[module].setPixmap(QPixmap(MODULE_STATUS_ARRAY[module, status]))
        # 模块进度
        if gif is None:
            self.__statusViewList[module].setPixmap(QPixmap(STATUS_ARRAY[status]))
            self.__statusViewList[module].resize(scaleSizeW(50), scaleSizeH(45))
        else:
            self.__statusViewList[module].setMovie(gif)
            self.__statusViewList[module].resize(scaleSizeW(50), scaleSizeH(45))

        # gif动画
        if gif is not None:
            gif.start()

    @main_thread
    def update_module(self, module):
        """
        更新模块进度
        :param module: 当前模块
        """
        log("update_module", module)
        # 初始化界面
        self.progressBar_2.setValue(0)
        self.progressBar_3.setValue(0)
        # 本模块提示自检中
        self.update_module_status(module, STATUS_RUNNING)
        # 总体进度
        self.__totalTarget = 100 / len(MODULE_STATUS_ARRAY) * (module + 1)
        self.__totalTimer.start(TOTAL_INTERVAL)
        # 开始更新
        self.__currentModule = module
        self.__moduleTimer.start(MODULE_INTERVAL)

    @main_thread
    def close_dialog(self):
        if self.installDialog is not None:
            self.installDialog.close()

    def __update_module(self):
        """
        槽函数，更新模块动画
        更新圆形进度条，同时刷新波浪进度
        将顺滑的更新到100%，结束后发送模块动画结束的信号
        """
        # 当前应更新值
        current = self.progressBar_2.Value + 1
        if current > 100:
            # 停止定时器 并 发送信号
            self.__moduleTimer.stop()
            self.module_animation_finish_signal.emit()
            return
        # 更新
        self.progressBar_2.setValue(current)
        self.progressBar_3.setValue(current)

    def __update_total(self):
        """
        更新整体进度
        """
        # 当前应更新值
        current = self.progressBar.value() + 1
        if current > self.__totalTarget or current > 100:
            # 停止定时器
            self.__totalTimer.stop()
            return
        # 更新
        self.progressBar.setValue(current)

    def show_tip(self, msg):
        """
        显示提示信息
        :param msg: 提示信息
        """
        self.label_tip.show()
        self.label_tip.setText(msg)

    def hide_tip(self):
        """
        隐藏提示信息
        """
        self.label_tip.hide()
        self.label_tip.setText("")
