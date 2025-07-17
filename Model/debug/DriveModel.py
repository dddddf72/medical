import threading
import time

import numpy as np
from PyQt5.QtCore import QThread, pyqtSignal
from numpy import array

from Config.Config import config
from Model.abstract.DriveModel import DriveModelAbstract
from Utils.Log import log

# 偏置电压取值次数
OFFSET_TIMES = config.offset_times
# 偏置电压正常范围，单位：V，超过此范围，判定apd异常
OFFSET_MIN_CORRECT = -0.3
OFFSET_MAX_CORRECT = 0.3
# 偏置电压范围
OFFSET_MIN = config.offset_min
OFFSET_MAX = config.offset_max
# 预热时长，单位：分钟
PREHEAT_TIME = config.preheat_time


class DriveModel(DriveModelAbstract):
    """
    兼容实体手柄按键
    """
    def __init__(self, presenter):
        super().__init__(presenter)
        self.__dataAcqThread = None

    def get_ni_info(self) -> str:
        if self.__dataAcqThread is not None:
            return self.__dataAcqThread.get_info()
        else:
            return "模拟数据"

    def start_up_laser(self):
        log("start_up_laser", True)
        return True

    def get_laser_power(self):
        log("get_laser_power", 21)
        return 21

    def start_acq(self, slot):
        # 已打开
        if self.__dataAcqThread is not None:
            return

        # 创建线程
        self.__dataAcqThread = DataAcqThread(slot)
        # 开始采集
        self.__dataAcqThread.start()

    def light_switch(self, enable):
        super(DriveModel, self).light_switch(enable)
        log("light_switch", enable)

    @property
    def apd_status(self):
        """
        实际不会调用
        """
        return True

    @property
    def ni_status(self):
        """
        实际不会调用
        """
        return True

    def lamp_switch(self, lamp_1, lamp_2):
        # log("lamp_switch", "lamp_1: %s lamp_2: %s" % (lamp_1, lamp_2))
        pass


# 数据采集线程周期监测的周期时长，单位：秒
MONITOR_CYCLE_TIME = 10

# 测试荧光数据
TEST_VALUE_LIST = [
    0.6,
    0.5,
    0.4,
    0.5,
    0.6,
    0.55,
    0.48,
    4,
    0.9,
    1.8,
    0.1,
    6,
    20
]
# 是否使用固定值
# False: 使用 TEST_VALUE_LIST
# True: 使用TEST_VALUE_LIST[0]
FIXED_ENABLE = False


class DataAcqThread(QThread):
    """
    数据采样线程
    """
    # 数据信号
    dataSignal = pyqtSignal(float)

    def __init__(self, slot):
        super(DataAcqThread, self).__init__()
        self.__refreshTime = 0.02
        # 取值索引
        self.__index = 0
        log("debug DataAcqThread", "debug模式下的数据采集线程")
        log("DataAcqThread refreshTime", self.__refreshTime)
        # 上次周期监测的时间戳，单位为秒
        self.lastMonitorTicks = None
        # 绑定信号
        self.dataSignal.connect(slot)

        # 用于测试的数据，缺乏数据采集卡时调试测试用
        # 偏置电压，单位：V，初始化 0V，将在第一次读取时更新
        self.__voltageOffset = 0
        # 偏置电压是否更新标记
        self.__offsetRefresh = False
        # 原始数据的均值
        self.__originalAvgData = None
        # 最终值
        self.__finalData = None

    def run(self):
        while 1:
            # 当前值
            self.__originalAvgData = TEST_VALUE_LIST[0]
            # 不使用固定值
            if not FIXED_ENABLE:
                self.__originalAvgData = TEST_VALUE_LIST[self.__index % len(TEST_VALUE_LIST)]
                self.__index += 1

            # 首次采集需更新偏置电压
            if not self.__offsetRefresh:
                self.__first_update_offset()

            # 最终值
            self.__finalData = abs(self.__originalAvgData - self.__voltageOffset)

            # 周期监测
            self.monitor_cycle(self.__finalData)
            # 发送信号
            self.dataSignal.emit(self.__finalData)
            # 休眠一段时间后刷新
            time.sleep(self.__refreshTime)

    def monitor_cycle(self, data):
        """
        周期监测
        :param data: 采集数据
        """
        # 首次运行不做监测
        if self.lastMonitorTicks is None:
            self.lastMonitorTicks = time.time()
            return

        # 未达监测周期
        if (time.time() - self.lastMonitorTicks) < MONITOR_CYCLE_TIME:
            return

        # 已达监测周期，更新监测时间
        self.lastMonitorTicks = time.time()
        # 打印数据
        log("DataAcqThread data", self.get_info())

    def get_info(self) -> str:
        """
        获取线程信息
        :return: 信息
        """
        return "模拟数据 [原始x = %.4f] [偏置y = %.4f] [x - y = %.4f] [最终 = %.4f]" % (
            self.__originalAvgData,
            self.__voltageOffset,
            self.__originalAvgData - self.__voltageOffset,
            self.__finalData
        )

    def __first_update_offset(self):
        """
        首次更新偏置电压
        """
        # 已更新
        if self.__offsetRefresh:
            log("DataAcqThread error", "偏置电压已更新，不得调用 first_update_offset")
            return

        self.__offsetRefresh = True
        log("DataAcqThread 首次采集值", self.__originalAvgData)

        # 偏置电压取值次数为 0，表示不需要采集偏置电压
        if OFFSET_TIMES == 0:
            self.__voltageOffset = 0
            log("DataAcqThread", "offset_times = 0 -> voltageOffset = 0")
            return

        # 采集偏置电压相关信息
        log(
            "DataAcqThread 采集偏置电压配置",
            "[offset_times = %d] [offset_min = %.3f] [offset_max = %.3f]" % (
                OFFSET_TIMES, OFFSET_MIN, OFFSET_MAX
            )
        )
        log(
            "DataAcqThread 偏置电压正常范围",
            "[offset_min_correct = %.3f] [offset_max_correct = %.3f]" % (
                OFFSET_MIN_CORRECT, OFFSET_MAX_CORRECT
            )
        )

        # 需要采集
        self.__update_offset_thread()

    def __update_offset_thread(self, offset_list: array = None):
        """
        更新偏置电压的线程
        :param offset_list: 采集到的偏置电压值
        """
        # 新增偏置电压
        nowOffset = self.__originalAvgData
        offset_list = np.asarray([nowOffset]) if offset_list is None else np.append(offset_list, nowOffset)

        # 偏置电压合法性判断
        if not (OFFSET_MIN <= nowOffset <= OFFSET_MAX):
            log("DataAcqThread error 采集到需过滤的异常偏置电压", nowOffset)

        # where 返回符合条件的元素的索引构成的元组；offset_list[元组]，将对应元素选出
        legalList = offset_list[
            np.where((OFFSET_MIN <= offset_list) & (offset_list <= OFFSET_MAX))
        ]
        # 更新偏置电压，-0 将 ndarray 转为 float。
        self.__voltageOffset = self.__voltageOffset if len(legalList) <= 0 else np.mean(legalList) - 0

        log(
            "DataAcqThread",
            "[offset = %.4f] [len OffsetList = %d] [OffsetList = %s]" % (
                self.__voltageOffset, len(offset_list), " | ".join(map(str, offset_list))
            )
        )

        # 每次采集都检查apd是否异常，以便及时发现问题
        if not (OFFSET_MIN_CORRECT <= nowOffset <= OFFSET_MAX_CORRECT):
            self.__apd_status = False
            log("DataAcqThread error 采集到超过正常范围的偏置电压，判定apd异常", nowOffset)

        # 已达采集限制次数，不再循环采集
        if len(offset_list) >= OFFSET_TIMES:
            log("DataAcqThread 偏置电压采集完成")

            # apd 状况检查
            if not np.all((OFFSET_MIN_CORRECT <= offset_list) & (offset_list <= OFFSET_MAX_CORRECT)):
                # 不是全在正常范围
                self.__apd_status = False
                log("DataAcqThread error 偏置电压采集列表中存在超过正常范围的值，判定apd异常")
            # apd是否无数据输入
            if np.all(abs(offset_list) <= 1e-4):
                # 所有数据的绝对值都接近0
                self.__apd_status = False
                log("DataAcqThread error 偏置电压所有数据绝对值都接近0，判定apd异常")

            # 已达采集限制次数，不再循环采集
            return

        # 进行下一轮更新
        threading.Timer(
            PREHEAT_TIME * 60 / OFFSET_TIMES,
            self.__update_offset_thread,
            args=(offset_list,)).start()

