import time

from PyQt5.QtGui import QPixmap

from Utils.Log import log
from Utils.Path import rootPath
from View.BaseView import BaseView, main_thread
# 图片所在路径
from View.config.ConfigView import ConfigView

imgPath = rootPath + "/View/img/common"

# 后门按钮点击激活次数
BACK_DOOR_CLICK_TOTAL = 5
# 进入后门的点击的有效间隔时长，单位：秒，超时前面的点击将无效
BACK_DOOR_CLICK_TIME = 5


class ReleaseBaseView(BaseView):
    """
    release view 模块的基类
    """

    def __init__(self, presenter):
        super().__init__(presenter)
        # 后门按钮点击计数
        self.__backDoorClickCount = 0
        # 后门按钮最新一次点击时间
        self.__backDoorClickTime = time.time()
        # 后门打开的配置界面
        self.__configView = None

    def back_door_enable(self):
        """
        后门使能
        """
        # 后门按钮点击事件
        self.back_door_btn.clicked.connect(self.__back_door_btn_click)

    def __back_door_btn_click(self):
        """
        后门按钮点击
        连续点击若干次，打开后门界面
        """
        # 超时，之前的点击无效
        if time.time() - self.__backDoorClickTime > BACK_DOOR_CLICK_TIME:
            self.__backDoorClickCount = 0

        # 更新
        self.__backDoorClickCount += 1
        self.__backDoorClickTime = time.time()
        log("__back_door_btn_click", self.__backDoorClickCount)

        if self.__backDoorClickCount % BACK_DOOR_CLICK_TOTAL == 0:
            self.__configView = ConfigView()
            self.__configView.show()

    @main_thread
    def error(self, msg):
        super(ReleaseBaseView, self).error(msg)

    @main_thread
    def tip(self, msg):
        super(ReleaseBaseView, self).tip(msg)

    def show(self):
        """
        重写显示函数
        """
        self.showFullScreen()

    def _value_to_text(self, value):
        """
        将荧光值数值转为界面显示的文本

        小数点后保留三位，小数点前保留两位
        并去除小数点
        如 110.5427 -> 10542
        :param value: 荧光数值
        :return: 文本
        """
        # 丢弃无用整数位
        value = value / 100 - int(value / 100)
        # 丢弃无用小数位
        valueText = format(value, ".5f")
        # 只要小数点后的五位数字
        return str(valueText)[2:7]

    def light_switch_callback(self, enable):
        """
        光开关控制的回调通知
        每个界面都应该有本函数的处理
        :param enable: 允许光通过：True
        """
        img = imgPath + "/light_switch_false.png"
        # 需显示打开
        if enable:
            img = imgPath + "/light_switch_true.png"

        self.label_light_switch.setPixmap(QPixmap(img))
