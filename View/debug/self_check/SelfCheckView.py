from PyQt5.QtCore import QTimer
from numpy import array

from Utils.Log import log
from View.BaseView import main_thread
from View.abstract.SelfCheckView import SelfCheckViewAbstract, MODULE_LOG_ARRAY, STATUS_LOG_ARRAY, \
    DETAILED_MODULE_ERROR_ARRAY
from View.debug.DebugBaseView import DebugBaseView
from View.debug.self_check import self_check


class SelfCheckView(SelfCheckViewAbstract, self_check.Ui_MainWindow, DebugBaseView):
    @main_thread
    def boot_check_success(self):
        log("boot_check_success", "自检正常")
        self.logTextBrowser.append("自检完成，设备正常")
        self.logTextBrowser.append("请安装无菌护套，装配完成后点击装配完成按钮")

    @main_thread
    def mode_open_check_success(self):
        log("mode_open_check_success", "自检正常")

    @main_thread
    def check_error(self, detailed_module_status_list: array):
        error = super(SelfCheckView, self).check_error(detailed_module_status_list)
        self.logTextBrowser.append("异常信息")
        self.logTextBrowser.append(error)

    def _refresh_config(self):
        # 用于测试的model层
        model = self.presenter.get_self_check_model_test()

        # 配置信息
        self.openLineEdit.setReadOnly(True)
        self.openLineEdit.setText(str(self.presenter.get_is_mode_key_open()))
        self.rfidLineEdit.setReadOnly(True)
        self.rfidLineEdit.setText("test")
        self.differenceLineEdit.setReadOnly(True)
        self.differenceLineEdit.setText("test")
        self.laserLineEdit.setReadOnly(True)
        self.laserLineEdit.setText(str(model.laser_device_status()))
        self.lightLineEdit.setReadOnly(True)
        self.lightLineEdit.setText(str(model.light_switch_status()))
        self.apdLineEdit.setReadOnly(True)
        self.apdLineEdit.setText(str(model.apd_status()))

    def _init_ui(self):
        # 信号连接信号槽
        self.rfidPushButton.clicked.connect(self.__rfid_btn_click)
        self.readPushButton.clicked.connect(self.__read_btn_click)
        self.installPushButton.clicked.connect(self.__install_btn_click)
        self.quickCheckPushButton.clicked.connect(self.__quick_check_btn_click)

    def __rfid_btn_click(self):
        """
        点击RFID读取按钮
        """
        self.logTextBrowser.append("读取仿体内置荧光值")
        log("读取仿体内置荧光值")

    def __read_btn_click(self):
        """
        点击探头取值按钮
        """
        self.logTextBrowser.append("探头取值")
        log("探头取值")

    def __install_btn_click(self):
        """
        点击装备完成按钮
        """
        self.logTextBrowser.append("装备完成")
        log("装备完成")
        self.presenter.install_complete()

    def __quick_check_btn_click(self):
        """
        点击快速自检按钮
        """
        self.logTextBrowser.append("快速自检")
        log("快速自检")
        self.presenter.boot_check()

    @main_thread
    def update_module_status(self, module, status):
        super(SelfCheckView, self).update_module_status(module, status)
        self.logTextBrowser.append("update_module_status %s, %s" % (MODULE_LOG_ARRAY[module], STATUS_LOG_ARRAY[status]))

    @main_thread
    def update_module(self, module):
        """
        需要为耗时操作不能立刻回调self.presenter.module_check()
        """
        log("update_module", module)
        self.logTextBrowser.append("update_module: %d" % module)
        QTimer(self).singleShot(1000, self.presenter.module_check)

    @main_thread
    def close_dialog(self):
        pass
