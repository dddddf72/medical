import abc

from PyQt5 import QtCore

from View.BaseView import BaseView


class CollectViewAbstract(BaseView):
    """
    检测采集界面
    """
    # 信号
    refresh_value_signal = QtCore.pyqtSignal(float)
    close_dialog_signal = QtCore.pyqtSignal()

    def __init__(self, presenter, referent_value):
        # 保存基准值
        self._referentValue = referent_value

        super().__init__(presenter)

        # 信号绑定
        self.refresh_value_signal.connect(self.refresh_value)
        self.close_dialog_signal.connect(self.close_dialog)

    @abc.abstractmethod
    def refresh_value(self, value):
        """
        刷新荧光值
        :param value: 荧光值
        """
        pass

    @abc.abstractmethod
    def close_dialog(self):
        """
        关闭所有dialog
        """
        pass
