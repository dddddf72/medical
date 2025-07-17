import abc

from PyQt5.QtCore import QObject

from Drive.DriveManager import driveManager

# 时间间隔，单位：秒
# 调用函数时携带生成器并等待函数控制迭代时
# 需要延时执行，确保generator不在运行中
# 注意，若在debug时在yield处打了断点，延时启动已执行，依旧产生generator运行中的错误，但不影响生产
# 参考MainPresenter.__power_up_init_generator 中的使用
GENERATOR_EXEC_DELAY = 0.001


class BasePresenter(QObject):
    """
    P层的基类，所有P层继承本类
    """
    @abc.abstractmethod
    def show(self, *args):
        """
        显示本层的核心界面
        """
        # 注册模式键长按事件
        driveManager.register_mode_long_click_callback(self._mode_long_click)

    def _close(self):
        """
        回收
        """
        # 模式键长按按事件取绑
        driveManager.unbound_mode_long_click_callback(self._mode_long_click)

    def close(self):
        """
        关闭
        TODO MS 22.2.10 临时使用
        """
        self._close()

    @property
    @abc.abstractmethod
    def _view(self):
        """
        核心V层
        :return: 核心V层
        """
        pass

    def _mode_long_click(self):
        """
        模式键长按
        TODO MS 22.3.28 当前模式键长按将直接打开取基准值界面
        """
        # 模式键选择
        self._view.mode_choice(None)
