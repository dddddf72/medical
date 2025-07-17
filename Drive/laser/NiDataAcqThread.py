import threading
import time

import nidaqmx
import numpy as np
from PyQt5.QtCore import QThread, pyqtSignal
from nidaqmx.constants import TerminalConfiguration, Edge, AcquisitionType
from numpy import array

from Config.Config import config
from Utils.Log import log

# 周期监测的周期时长，单位：秒
MONITOR_CYCLE_TIME = 10
# 偏置电压正常范围，单位：V，超过此范围，判定apd异常
OFFSET_MIN_CORRECT = -0.3
OFFSET_MAX_CORRECT = 0.5
# 偏置电压取值次数。偏置电压的取值是在预热阶段，所以取值间隔 = 预热时长 / 偏置电压取值次数
OFFSET_TIMES = config.offset_times
# 偏置电压范围，单位：V，超过此范围将被过滤
OFFSET_MIN = config.offset_min
OFFSET_MAX = config.offset_max
# 预热时长，单位：分钟。apd状态的判定必须保证偏置电压最终取值的耗时小于系统预热时长，否则异常结果来不及送出，自检却已通过。
PREHEAT_TIME = config.preheat_time


def get_ni_ratio():
    """
    :return: 采集数据的系数
    """
    return config.ni_ratio


def get_ni_compensate():
    """
    :return: 采集数据的补偿
    """
    return config.ni_compensate


def get_ni_device_id():
    """
    :return: 数据采集卡设备id
    """
    return config.ni_device_id


class NiDataAcqThread(QThread):
    """
    数据采样线程
    """
    # 数据信号
    dataSignal = pyqtSignal(float)

    def __init__(
            self,
            slot,
            acq_rate=48000,
            avg_times=80,
            refresh_time=0.02,
            device_id=get_ni_device_id()
    ):
        """
        :param slot: 信号槽函数
        :param acq_rate: 采样率
        :param avg_times: 平均次数
        :param refresh_time: 刷新时间，单位：秒，每隔一段时间刷新数据
        :param device_id: 数据采集卡id，根据 usb端口 和 通道 决定
        """
        super(NiDataAcqThread, self).__init__()
        # 数据存储
        self.__acqRate = acq_rate
        self.__avgTimes = avg_times
        self.__refreshTime = refresh_time
        self.__deviceId = device_id
        log(
            "NiDataAcqThread",
            "采样率: %d; 平均次数: %d; 刷新时间: %f; 数据采集卡: %s"
            % (acq_rate, avg_times, refresh_time, device_id)
        )

        # 绑定信号
        self.dataSignal.connect(slot)

        # 数据采集卡初始化状态，由初始化判定。默认异常，初始化成功才判定正常
        self.__ni_status = False
        # apd状态，由偏置电压情况进行判定。默认正常，发现异常状况才判定异常
        self.__apd_status = True

        # 其他数据
        # 偏置电压，单位：V，初始化 0V，将在第一次读取时更新
        self.__voltageOffset = 0
        # 偏置电压是否更新标记
        self.__offsetRefresh = False
        # 原始数据
        self.__originalData = None
        # 原始数据的均值
        self.__originalAvgData = None
        # 最终值，final = abs|(originalAvg - offset) * ratio + compensate|
        self.__finalData = None
        # 上次周期监测的时间戳，单位为秒
        self.lastMonitorTicks = None

    def run(self):
        with nidaqmx.Task() as task:
            # 采样设备配置
            # 如果配置失败，可以尝试重新配置一次，以便自动修改id时生效
            if not self.__ni_configure(task):
                self.__ni_configure(task)

            # 死循环采集数据
            while 1:
                # 采集数据
                if self.__ni_status:
                    try:
                        self.__originalData = task.read(self.__avgTimes)
                    except BaseException as error:
                        self.__originalData = [0]
                        log("error NiDataAcqThread", "数据采集器读值异常，请检查设备连接情况。在软件启动前插入USB将导致读值异常。可拔除USB设备后重启或更换采集卡USB端口解决")
                        print(repr(error))
                        log(error)
                else:
                    self.__originalData = [0]

                # 平均值
                self.__originalAvgData = np.mean(self.__originalData)

                # 首次采集需更新偏置电压
                if not self.__offsetRefresh:
                    self.__first_update_offset()

                # 考虑偏置电压，保留四位小数，其他截断
                self.__finalData = float("%.4f" % (self.__originalAvgData - self.__voltageOffset))
                # 系数与补偿
                self.__finalData = abs(self.__finalData * get_ni_ratio() + get_ni_compensate())
                # 周期监测
                self.monitor_cycle()
                # 发送信号
                self.dataSignal.emit(self.__finalData)
                # 休眠一段时间后刷新
                time.sleep(self.__refreshTime)

    def monitor_cycle(self):
        """
        周期监测
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
        log("NiDataAcqThread 单位: V 算法", "final = abs|(originalAvg - offset) * ratio + compensate|")
        log("NiDataAcqThread 信息", self.get_ni_info())
        log("NiDataAcqThread 系数", get_ni_ratio())
        log("NiDataAcqThread 补偿", get_ni_compensate())
        log("NiDataAcqThread 原始数据", " | ".join(map(str, self.__originalData)))

    @property
    def apd_status(self) -> bool:
        """
        本状态需要在预热结束后获取
        """
        return self.__apd_status

    @property
    def ni_status(self) -> bool:
        """
        本状态需要在激光发生器正常打开，数据采集线程初始化运行 之后获取
        """
        return self.__ni_status

    def __ni_configure(self, task):
        """
        数据采集卡的配置
        :param task:
        :return: 配置结果，成功返回True
        """
        try:
            # 打开ai0通道，需要用差分输入，单端参考输入
            task.ai_channels.add_ai_voltage_chan(
                self.__deviceId,
                terminal_config=TerminalConfiguration.DIFFERENTIAL
            )
            # 采样配置
            task.timing.cfg_samp_clk_timing(
                self.__acqRate,
                "",
                Edge.RISING,
                AcquisitionType.FINITE,
                self.__avgTimes
            )
            self.__ni_status = True

        except BaseException as error:
            self.__ni_status = False
            log("error NiDataAcqThread", "数据采集器初始化异常，请检查设备连接情况 或 数据采集卡设备id")
            print(repr(error))
            log(error)

            # 尝试自动修改采集卡设备id
            errorMsg = str(error)
            # 设备建议
            suggestedIndex = errorMsg.find("Suggested")
            if suggestedIndex == -1:
                log("error NiDataAcqThread", "自动修改数据采集卡设备id失败，无可供参考的id，请检查硬件或驱动情况")

            else:
                # 整理设备建议列表
                suggestedList = errorMsg[suggestedIndex:].split("\n")[0].split(': ')[1].split(', ')
                # 修改配置
                deviceId = suggestedList[-1] + "/ai0"
                config.set_ni_device_id(deviceId)
                self.__deviceId = deviceId
                log("NiDataAcqThread", "已自动修改数据采集卡设备id为：" + deviceId)
                log("NiDataAcqThread", "采集卡设备数量：%s，请确认是否为对应采集卡" % str(len(suggestedList)))

        # 配置结果
        return self.__ni_status

    def get_ni_info(self) -> str:
        """
        获取数据采集卡的信息
        :return: 数据采集卡信息
        """
        return "[原始x = %.4f] [偏置y = %.4f] [x - y = %.4f] [最终 = %.4f]" % (
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
            log("NiDataAcqThread error", "偏置电压已更新，不得调用 first_update_offset")
            return

        self.__offsetRefresh = True
        log("NiDataAcqThread 首次采集值", self.__originalAvgData)

        # 偏置电压取值次数为 0，表示不需要采集偏置电压
        if OFFSET_TIMES == 0:
            self.__voltageOffset = 0
            log("NiDataAcqThread", "offset_times = 0 -> voltageOffset = 0")
            return

        # 采集偏置电压相关信息
        log(
            "NiDataAcqThread 采集偏置电压配置",
            "[offset_times = %d] [offset_min = %.3f] [offset_max = %.3f]" % (
                OFFSET_TIMES, OFFSET_MIN, OFFSET_MAX
            )
        )
        log(
            "NiDataAcqThread 偏置电压正常范围",
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
            log("NiDataAcqThread error 采集到需过滤的异常偏置电压", nowOffset)

        # where 返回符合条件的元素的索引构成的元组；offset_list[元组]，将对应元素选出
        legalList = offset_list[
            np.where((OFFSET_MIN <= offset_list) & (offset_list <= OFFSET_MAX))
        ]
        # 更新偏置电压，-0 将 ndarray 转为 float。
        self.__voltageOffset = self.__voltageOffset if len(legalList) <= 0 else np.mean(legalList) - 0

        log(
            "NiDataAcqThread",
            "[offset = %.4f] [len OffsetList = %d] [OffsetList = %s]" % (
                self.__voltageOffset, len(offset_list), " | ".join(map(str, offset_list))
            )
        )

        # 每次采集都检查apd是否异常，以便及时发现问题
        if not (OFFSET_MIN_CORRECT <= nowOffset <= OFFSET_MAX_CORRECT):
            self.__apd_status = False
            log("NiDataAcqThread error 采集到超过正常范围的偏置电压，判定apd异常", nowOffset)

        # 已达采集限制次数，不再循环采集
        if len(offset_list) >= OFFSET_TIMES:
            log("NiDataAcqThread 偏置电压采集完成")

            # apd 状况检查
            if not np.all((OFFSET_MIN_CORRECT <= offset_list) & (offset_list <= OFFSET_MAX_CORRECT)):
                # 不是全在正常范围
                self.__apd_status = False
                log("NiDataAcqThread error 偏置电压采集列表中存在超过正常范围的值，判定apd异常")
            # apd是否无数据输入
            if np.all(abs(offset_list) <= 1e-4):
                # 所有数据的绝对值都接近0
                self.__apd_status = False
                log("NiDataAcqThread error 偏置电压所有数据绝对值都接近0，判定apd异常")

            # 已达采集限制次数，不再循环采集
            return

        # 进行下一轮更新
        threading.Timer(
            PREHEAT_TIME * 60 / OFFSET_TIMES,
            self.__update_offset_thread,
            args=(offset_list,)).start()
