import abc

from PyQt5 import QtCore

from View.BaseView import BaseView, main_thread


class ReferentViewAbstract(BaseView):
    """
    取基准值界面实现
    """
    # 信号
    reference_value_progress_signal = QtCore.pyqtSignal(float, int, int)
    open_collect_signal = QtCore.pyqtSignal()
    scroll_bar_show_signal = QtCore.pyqtSignal(bool)

    def __init__(self, presenter):
        super().__init__(presenter)
        # 信号绑定
        self.reference_value_progress_signal.connect(self.reference_value_progress)
        self.open_collect_signal.connect(self.open_collect)
        self.scroll_bar_show_signal.connect(self.scroll_bar_show)

    @abc.abstractmethod
    def reference_value_progress(self, reference_value, times, tries_limit):
        """
        取基准值进度

        :param reference_value: 基准值
        :param times: 当前次数，>=1
        :param tries_limit: 限制次数，小于等于0为不限制次数（补值操作时）
        """
        pass

    @main_thread
    def open_collect(self):
        """
        打开采集界面
        """
        self.presenter.open_collect()

    @main_thread
    def scroll_bar_show(self, show_enable):
        """
        显示滚动条
        :param show_enable: 是否显示
        """
        pass
