import abc

from Model.BaseModel import BaseModel
from Utils.Log import log
from Utils.SoundUtil import SoundUtil, DI_MP3

# 瞬间播放的时长，单位：秒
PLAY_SECOND_TIME = 0.3


class DriveModelAbstract(BaseModel):
    """
    驱动的Model

    做一些初始化的操作为主，具体的驱动操作仍由各界面对应的 Model 处理
    当前仅由DriveManager初始化持有，当单例使用，除了初始化和驱动使用，其他地方不该调用
    """
    def __init__(self, presenter):
        super().__init__(presenter)
        # 光开关回调，在光开光发生动作时，回调
        self.__lightSwitchCallback = None
        # 提示声工具
        self.__diUtil = SoundUtil(DI_MP3, PLAY_SECOND_TIME)

    @abc.abstractmethod
    def start_up_laser(self):
        """
        启动激光发生器
        :return: 启动结果
        """
        pass

    @abc.abstractmethod
    def get_laser_power(self):
        """
        获取激光功率
        :return: 激光功率，获取失败返回-1
        """
        pass

    @abc.abstractmethod
    def start_acq(self, slot):
        """
        开始数据采集
        :param slot: 槽函数，将绑定数据采集的信号（pyqtSignal(float)），获取到数据
        """
        pass

    @abc.abstractmethod
    def apd_status(self):
        """
        apd状态
        :return: apd状态
        """
        pass

    @abc.abstractmethod
    def ni_status(self):
        """
        数据采集卡状态
        :return: 正常返回True
        """
        pass

    @abc.abstractmethod
    def light_switch(self, enable):
        """
        光开关控制
        :param enable: 允许光通过：True
        """
        # 提示音
        if enable:
            self.__diUtil.play_second()

        # 回调光开关函数
        if self.__lightSwitchCallback is not None:
            self.__lightSwitchCallback(enable)

    def register_light_switch_callback(self, callback):
        """
        注册光开关回调
        :param callback: 回调函数
        """
        log("register_light_switch_callback", callback)
        self.__lightSwitchCallback = callback

    def unbound_light_switch_callback(self, callback):
        """
        取消绑定光开关
        :param callback: 被取绑的回调函数，若没有，则不取消绑定
        """
        if self.__lightSwitchCallback == callback:
            log("unbound_light_switch_callback", callback)
            self.__lightSwitchCallback = None

    @abc.abstractmethod
    def get_ni_info(self) -> str:
        """
        获取数据采集卡的信息
        :return: 数据采集卡信息
        """
        pass

    @abc.abstractmethod
    def lamp_switch(self, lamp_1, lamp_2):
        """
        手柄灯控制
        :param lamp_1: 手柄灯1
        :param lamp_2: 手柄灯2
        """
        pass
