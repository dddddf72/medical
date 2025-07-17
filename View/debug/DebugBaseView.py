import abc

from View.BaseView import BaseView, main_thread


class DebugBaseView(BaseView):
    """
    debug view 模块的基类
    """

    @main_thread
    def tip(self, msg):
        super(DebugBaseView, self).tip(msg)
        self.logTextBrowser.append("操作提示：" + msg)

    @main_thread
    def error(self, msg):
        super(DebugBaseView, self).error(msg)
        self.logTextBrowser.append("错误提示：" + msg)

    @abc.abstractmethod
    def _refresh_config(self):
        """
        刷新配置信息
        """
        pass

    def show(self):
        """
        重写显示函数
        加载部分数据
        """
        super().show()
        # 加载配置数据
        self._refresh_config()

    def light_switch_callback(self, enable):
        """
        光开关控制的回调通知
        每个界面都应该有本函数的处理
        :param enable: 允许光通过：True
        """
        self.tip("light_switch_callback: %s" % str(enable))
