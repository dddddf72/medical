from Utils.Log import log
from View.BaseView import main_thread
from View.abstract.ReferentView import ReferentViewAbstract
from View.debug.DebugBaseView import DebugBaseView
from View.debug.referent import referent


class ReferentView(ReferentViewAbstract, referent.Ui_MainWindow, DebugBaseView):
    def _init_ui(self):
        # 信号连接信号槽
        self.readPushButton.clicked.connect(self.__read_btn_click)
        self.refreshPushButton.clicked.connect(self._refresh_config)

    def _refresh_config(self):
        self.logTextBrowser.append("刷新配置")

        # 用于测试的model层
        model = self.presenter.get_referent_model_test()

        # 配置信息
        self.openLineEdit.setReadOnly(True)
        self.openLineEdit.setText(str(self.presenter.get_is_mode_key_open()))
        self.referenceLineEdit.setReadOnly(True)
        self.referenceLineEdit.setText("value")
        self.minLineEdit.setReadOnly(True)
        self.minLineEdit.setText(str(self.presenter.referent_min))
        self.maxLineEdit.setReadOnly(True)
        self.maxLineEdit.setText(str(self.presenter.referent_max))
        self.multipleLineEdit.setReadOnly(True)
        self.multipleLineEdit.setText("倍数")

    @main_thread
    def reference_value_progress(self, reference_value, times, tries_limit):
        self.logTextBrowser.append(
            "基准值：%s; 进度: %d / %d"
            % (str(reference_value), times, tries_limit)
        )

    def __read_btn_click(self):
        """
        点击探头取值按钮
        """
        self.logTextBrowser.append("探头取值")
        log("探头取值")
        self.presenter.confirm_referent(0.5)
