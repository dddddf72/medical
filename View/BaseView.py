import abc
import threading

from PyQt5 import QtCore
from PyQt5.QtCore import QTimer
from PyQt5.QtWidgets import QMainWindow

from Utils.Log import log


def main_thread(func):
    """
    用于装饰V层提供给P层使用的界面更新函数

    需装饰在实现层，若装饰在Abstract层将无效

    P层调用V层的函数时可能处于子线程中
    为避免更新异常，将通过信号通知主线程更新界面

    注意： 被装饰的函数必须已被一个信号绑定
          信号的命名有规则限制，必须为：函数名_signal
          因为装饰器将根据反射获取信号（func.__name__ + "_signal"）
          参考：MainView.laser_power_check_progress_signal

    :param func: 被装饰的函数
    :return: handle
    """
    def handle(self, *args, **kwargs):
        """
        处理函数
        :param self: 第一个参数
        :param args: 被装饰的V层函数的参数
        :param kwargs: 被装饰的V层函数的参数
        """
        if threading.current_thread().name == "MainThread":
            # 是主线程，直接调用被装饰方法
            func(self, *args, **kwargs)
        else:
            # 不是主线程，通过信号通知主线程调用被装饰方法
            getattr(self, func.__name__ + "_signal").emit(*args, **kwargs)

    return handle


class BaseView(QMainWindow):
    """
    View层的基础抽象类，所有View继承本类实现
    """
    # 信号
    error_signal = QtCore.pyqtSignal(str)
    tip_signal = QtCore.pyqtSignal(str)
    mode_choice_signal = QtCore.pyqtSignal(object)

    def __init__(self, presenter):
        """
        需设置持有本V的P层
        """
        super().__init__()

        # 信号绑定
        self.error_signal.connect(self.error)
        self.tip_signal.connect(self.tip)
        self.mode_choice_signal.connect(self.mode_choice)

        self.presenter = presenter
        self.setupUi(self)
        self._init_ui()

        # 模式键打开的界面
        self.__modePresenter = None

    @abc.abstractmethod
    def error(self, msg):
        """
        错误提示
        :param msg: 提示信息
        """
        log("View error", msg)

    @abc.abstractmethod
    def tip(self, msg):
        """
        提示，用于操作提示
        :param msg: 提示信息
        """
        log("View tip", msg)

    @abc.abstractmethod
    def _init_ui(self):
        """
        初始化界面
        如信号连接信号槽；配置数据；启动必要操作等
        """
        pass

    @main_thread
    def mode_choice(self, referent_list):
        """
        模式键选择打开界面
        TODO MS 22.2.10 当前模式键选择将直接打开取基准值界面，并关闭本界面
        :param referent_list: 基准值列表，数组 或 None
        """
        # 数据处理
        if referent_list is None:
            referent_list = []

        # 延时关闭本界面
        QTimer(self).singleShot(1000, self.presenter.close)
        # 打开取基准值界面
        from Presenter.UpdateReferentPresenter import UpdateReferentPresenter
        self.__modePresenter = UpdateReferentPresenter(referent_list)
        self.__modePresenter.show()
