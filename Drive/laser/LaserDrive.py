import math
from ctypes import c_double, byref, c_int, windll

from Config.Config import config
from Utils.Log import log
from Utils.Path import rootPath

# dll库位置
LASER_DLL = rootPath + "/Drive/laser/dll/ohlaser.dll"
# 激光器设备索引
DEVICE_INDEX = int(0)


def get_laser_power():
    """
    获取设置的激光器功率
    :return: 激光器功率 = 激光器功率 + 激光器功率补偿值
    """
    return config.laser_power + config.laser_power_compensate


def simple_result(func):
    """
    结果解析装饰器
    用于装饰驱动操作的结果，适用于简单结果：True or False

    :param func: 被装饰的函数
    :return: handle
    """
    def handle(*args, **kwargs):
        """
        处理函数
        :param args: 被装饰函数的参数
        :param kwargs: 被装饰函数的参数
        :return: 被装饰函数的返回值解析后的结果，被装饰的函数将返回此结果
        """
        # 设备打开失败，无法执行操作
        self = args[0]
        if not self.open_device_result:
            log(func.__name__, "设备打开失败，无法执行操作")
            return False

        # 执行被装饰函数
        result = func(*args, **kwargs)
        # 结果
        resultBool = bool(result)
        log(func.__name__ + " result", "%s %s" % (resultBool, result))
        return resultBool

    return handle


class LaserDrive(object):
    """
    激光设备的驱动层
    """
    def __init__(self):
        # 激光dll库
        log("LASER_DLL", LASER_DLL)
        self.laserDll = windll.LoadLibrary(LASER_DLL)
        # 激光功率
        log("laserPower", get_laser_power())
        # 打开设备结果
        self.__open_device_result = False

    @property
    def open_device_result(self):
        """
        设备打开结果
        :return: 已经打开True
        """
        return self.__open_device_result

    def open_device(self):
        """
        打开设备
        :return: 成功：True
        """
        log("open_device")
        # 设备不存在，无法打开
        amount = 0
        try:
            amount = self.laserDll.enumerateDevices()
        except:
            pass
        log("设备数量", amount)
        if amount <= 0:
            return False

        # 打开设备
        result = self.laserDll.openDevice(DEVICE_INDEX)
        if result == 0:
            # 打开失败
            log("laser device open", "error")
            return False
        elif result == 1:
            # 打开成功
            log("laser device open", "success")
            self.__open_device_result = True
            return True
        else:
            # 未知或不是软件控制模式
            log("laser device open", "result=%d or 前不是软件控制模式" % result)
            return False

    @simple_result
    def set_enable(self, enable):
        """
        使能操作
        :param enable: 开启：True; 关闭：False
        :return: 操作成功：True; 操作失败：False
        """
        log("set_enable 激光设备", enable)
        return self.laserDll.setLaserEnable(DEVICE_INDEX, enable)

    @simple_result
    def set_power(self, power):
        """
        设置功率
        :param power: 功率
        :return: 操作成功：True; 操作失败：False
        """
        log("set_power", power)
        return self.laserDll.setLaserPower(DEVICE_INDEX, c_double(power))

    def get_power(self):
        """
        获取功率
        功率单位为mw，范围为[0, 500]
        :return: 功率，获取失败返回-1
        """
        # 设备打开失败，无法操作
        if not self.open_device_result:
            return -1

        # 获取功率
        power = c_double(-1)
        result = self.laserDll.getLaserPower(DEVICE_INDEX, byref(power))
        # 执行结果
        resultBool = bool(result)
        log("get_power result", "%s %s" % (resultBool, result))
        log("get_power value", power.value)
        # 获取成功
        if resultBool and not math.isnan(power.value):
            return power.value

        # 获取失败
        log("error power", power)
        # 使用电压计算
        log("error 使用电压计算功率代替")
        voltage = self.get_voltage()
        # 获取失败
        if voltage == -1:
            return -1
        # 计算功率
        return LaserDrive.voltage_to_power(voltage)

    def get_voltage(self):
        """
        获取电压
        电压单位为V，范围为[0, 2.5]
        :return: 电压，获取失败返回-1
        """
        # 设备打开失败，无法操作
        if not self.open_device_result:
            return -1

        # 获取电压
        voltage = c_double(-1)
        result = self.laserDll.getLaserVoltage(DEVICE_INDEX, byref(voltage))
        # 执行结果
        resultBool = bool(result)
        log("get_voltage result", "%s %s" % (resultBool, result))
        log("get_voltage value", voltage.value)
        if not resultBool or math.isnan(voltage.value):
            # 获取失败
            log("error voltage", voltage)
            return -1
        else:
            # 获取成功
            return voltage.value

    @staticmethod
    def voltage_to_power(voltage):
        """
        电压 转 功率
        两者在50mw以上时为线性关系，小功率时仅做参考
        :param voltage: 电压（单位：V）
        :return: 功率（单位：mw）
        """
        powerValue = voltage * 1000 / 5
        log("voltage: %s -> power: %s" % (voltage, powerValue))
        return powerValue

    @simple_result
    def close_device(self):
        """
        关闭设备
        :return: 操作成功：True; 操作失败：False
        """
        log("close_device")
        self.set_enable(False)
        return self.laserDll.closeDevice(DEVICE_INDEX)

    def get_laser_status(self):
        """
        获取激光器状态
        TODO MS 22.1.15 获取异常，疑似接口有问题，第一版不做处理，默认正常
        :return: 状态正常：True；状态异常：False
        """
        log("get_laser_status")
        # 设备打开失败，无法操作
        if not self.open_device_result:
            return False

        # 获取状态
        status = c_int(-1)
        result = self.laserDll.getLaserStatus(DEVICE_INDEX, byref(status))
        # 执行结果
        resultBool = bool(result)
        log("get_laser_status result", "%s %s" % (resultBool, result))
        log("get_laser_status status", status.value)

        return True
