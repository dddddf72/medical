from Config.Config import config
from Utils.Log import log
from View.BaseView import main_thread
from View.abstract.CollectView import CollectViewAbstract
from View.debug.DebugBaseView import DebugBaseView
from View.debug.collect import collect


class CollectView(CollectViewAbstract, collect.Ui_MainWindow, DebugBaseView):
    def _refresh_config(self):
        self.logTextBrowser.append("刷新配置")

        self.clickModeLineEdit.setReadOnly(True)
        self.clickModeLineEdit.setText("test")
        self.valueLineEdit.setReadOnly(True)
        self.valueLineEdit.setText("value")

    def _init_ui(self):
        # 信号连接信号槽
        self.readPushButton.clicked.connect(self.__read_btn_click)
        self.refreshPushButton.clicked.connect(self._refresh_config)
        self.continuePushButton.clicked.connect(self.__continue_btn_click)
        self.installPushButton.clicked.connect(self.__install_complete)
        self.reducePushButton.clicked.connect(self.__reduce_btn_click)
        self.addPushButton.clicked.connect(self.__add_btn_click)

    @main_thread
    def refresh_value(self, value):
        self.valueLineEdit.setText(str(value))

    @main_thread
    def close_dialog(self):
        pass

    def __read_btn_click(self):
        """
        点击探头取值按钮
        """
        self.logTextBrowser.append("探头取值")
        log("探头取值")

    def __continue_btn_click(self):
        """
        点击连台手术按钮
        """
        self.logTextBrowser.append("连台手术，装配完成后点击装配完成")
        log("连台手术")

    def __install_complete(self):
        """
        点击装配完成按钮
        """
        self.logTextBrowser.append("装配完成")
        log("装配完成")
        self.presenter.install_complete()

    def __reduce_btn_click(self):
        """
        降低音量
        """
        self.presenter.set_volume(config.volume - 0.1)
        self.logTextBrowser.append("降低音量：" + str(config.volume))

    def __add_btn_click(self):
        """
        增加音量
        """
        self.presenter.set_volume(config.volume + 0.1)
        self.logTextBrowser.append("增加音量：" + str(config.volume))
