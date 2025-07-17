import abc

from Model.BaseModel import BaseModel


class SelfCheckModelAbstract(BaseModel):
    """
    自检的Model
    """

    @abc.abstractmethod
    def rfid_read_preset_value(self, generator):
        """
        通过rfid获取仿体预设荧光值
        :param generator: 生成器，将通过生成器返回获取结果，负数为获取失败
        """
        pass

    @abc.abstractmethod
    def laser_device_status(self):
        """
        激光发生器状态
        :return: 正常返回True
        """
        pass

    @abc.abstractmethod
    def light_switch_status(self):
        """
        光开关状态
        :return: 正常返回True
        """
        pass

    @abc.abstractmethod
    def apd_status(self):
        """
        apd 模块状态
        :return: 正常返回True
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
    def lamp_reverse(self):
        """
        手柄灯闪烁，lamp_1_switch 常亮； lamp_2_switch 闪烁
        """
        pass
