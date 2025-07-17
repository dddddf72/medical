import threading
import time

import numpy as np

from Config.Config import config
from Drive.handle.HandleDrive import HandleDrive
from Utils.Log import log


def btn_enable(func):
    """
    按钮使能监控的装饰器
    :param func: 被装饰的按钮回调动作函数
    :return: dll
    """
    def handle(*args, **kwargs):
        """
        处理函数
        未使能将不调用被装饰函数
        :param args: 被装饰函数的参数
        :param kwargs: 被装饰函数的参数
        """
        # HandleDriveManager 对象
        self = args[0]
        # 按钮信息
        log(func.__name__ + " enable", self.button_enable)
        if self.button_enable:
            # 使能状态，可调用
            func(*args, **kwargs)

    return handle


def read_btn_enable(func):
    """
    检测键使能监控的装饰器
    :param func: 被装饰的按钮回调动作函数
    :return: dll
    """
    def handle(*args, **kwargs):
        """
        处理函数
        未使能将不调用被装饰函数
        :param args: 被装饰函数的参数
        :param kwargs: 被装饰函数的参数
        """
        # HandleDriveManager 对象
        self = args[0]

        # 检测键使能状态
        # 检测键正在短按读值时忽略其他事件
        # 按键有效 且 不在短按读值时 检测键有效
        read_enable = self.button_enable and not self.read_short_clicking

        # 按键信息
        log(func.__name__ + " enable", read_enable)
        # 根据使能状态决定调用
        if read_enable:
            # 使能状态，可调用
            func(*args, **kwargs)

    return handle


# 长按触发的时间，单位：秒
LONG_CLICK_TRIGGER_TIME = 3
# 一次短按读值的读取次数
READ_SHORT_CLICK_LIMIT = 3
# 一次短按读值每次读取的间隔时间，单位：秒
READ_SHORT_CLICK_INTERVAL = 0.1
# 短按读值的时间长度
READ_SHORT_CLICK_TIME = READ_SHORT_CLICK_LIMIT * READ_SHORT_CLICK_INTERVAL
# 长按回调间隔时间，单位：秒
READ_LONG_CALLBACK_INTERVAL = 0.2
# 模式键最近点击记录队列长度，当前只有双击，记录最多两个
MODE_CLICK_QUEUE_SIZE = 2
# 模式键连击之间的有效时间间隔，单位：秒
MODE_CONTINUITY_CLICK_INTERVAL = 1


def get_read_long_trigger():
    """
    :return: 长按读值触发时长
    """
    return config.read_long_trigger


class HandleDriveManager(object):
    """
    手柄驱动管理器
    """
    def __init__(self, drive_model, laser_drive_manager):
        self.__driveModel = drive_model
        self.__laserDriveManager = laser_drive_manager
        # 驱动
        self.__handleDrive = HandleDrive()

        # 是否已成功初始化的标志
        self.__initResult = False

        # 按钮是否使能，未使能将忽略所有按钮事件的回调
        self.__buttonEnable = False

        # 检测键单击短按时间，用于判断检测键是否在单击短按状态
        # 检测键是否在单击短按的状态，处于该状态时将忽略检测键新的按钮事件
        # 该状态是一个原子动作，必须完成才能执行其他步骤，且被他阻塞的其他事件将忽略
        self.__readShortPressTime = None
        # 检测键模拟按键按下状态
        self.__readSimulateBtnIsPress = False
        # 检测键长按检测的线程
        self.__readLongClickTriggerThread = None
        # 检测单击回调事件
        self.__readShortClickCallback = None
        # 检测长按回调事件
        self.__readLongClickCallback = None
        # 检测长按回调是否使能
        self.__readLongClickCallbackEnable = False
        # 上次长按回调的时间
        self.__lastReadLongCallbackTime = time.time()

        # 模式键
        # 模式键模拟按键按下状态
        self.__modeSimulateBtnIsPress = False
        # TODO MS 22.10.8 单击 与 三击 尚无实际应用，为简化起见，暂未实现该逻辑
        # 模式键单击回调事件
        self.__modeShortClickCallback = None
        # 模式键双击回调事件
        self.__modeDoubleClickCallback = None
        # 模式键长按回调事件
        self.__modeLongClickCallback = None
        # 模式键长按检测的线程
        self.__modeLongClickTriggerThread = None
        # 模式键按下记录队列
        self.__modeClickQueue = []

    def _init_drive(self):
        """
        初始化驱动
        """
        # 驱动已初始化
        if self.__initResult:
            return None

        # 注册荧光值更新回调
        self.__laserDriveManager.register_fluorescence_callback(self.__fluorescence_update)
        # 注册按钮事件回调
        self.handle_drive.register_btn_callback(
            self.__read_btn_press,
            self.__read_btn_bounce,
            self.__mode_btn_press,
            self.__mode_btn_bounce
        )
        # 初始化驱动
        self.handle_drive.init()

        # 初始化成功
        self.__initResult = True
        return None

    def __fluorescence_update(self, data):
        """
        荧光值更新时的回调
        :param data: 荧光值
        """
        # 200ms 回调一次，不够时间间隔的不回调
        if time.time() - self.__lastReadLongCallbackTime < READ_LONG_CALLBACK_INTERVAL:
            return

        self.__lastReadLongCallbackTime = time.time()

        # 回调使能 且 存在回调函数
        if self.__readLongClickCallbackEnable and self.__readLongClickCallback is not None:
            self.__readLongClickCallback(data)

    @property
    def handle_drive(self):
        return self.__handleDrive

    @property
    def read_short_clicking(self):
        return self.__readShortPressTime is not None\
            and time.time() - self.__readShortPressTime < READ_SHORT_CLICK_TIME

    def read_btn_is_press(self, log_enable=True):
        """
        检测键是否按下
        :param log_enable: 日志打印使能
        """
        # 模拟按键已经按下
        if self.__readSimulateBtnIsPress:
            return self.__readSimulateBtnIsPress

        # 实体按键情况，若不存在实体按键，则返回False
        return self.handle_drive.read_btn_is_press(log_enable)

    @read_btn_enable
    def __read_btn_press(self):
        """
        检测键被按下
        将打开光开关并启动一次短按读值，在短按读值期间忽略检测键的其他事件
        同时，如果长按使能，将启动长按探测线程
        """
        # 记录正在单击短按状态
        self.__readShortPressTime = time.time()

        # 开始间隔读值的线程
        self.read_short_click_thread()

        # 长按使能，开始长按检测线程
        if self.__readLongClickCallback is not None:
            if self.__readLongClickTriggerThread is not None:
                log("__read_btn_press", "清理可能存在的检测键旧长按检测线程")
                self.__readLongClickTriggerThread.cancel()

            log("检测键长按探测线程启动")
            self.__readLongClickTriggerThread = threading.Timer(
                get_read_long_trigger(),
                self.__read_long_click_trigger
            )
            self.__readLongClickTriggerThread.start()

    @read_btn_enable
    def read_simulate_btn_press(self):
        """
        检测模拟键被按下
        """
        # 检测模拟键被按下
        self.__readSimulateBtnIsPress = True
        # 调用按下流程
        self.__read_btn_press()

    @read_btn_enable
    def __read_btn_bounce(self):
        """
        检测键弹起
        """
        # 终止长按检测的线程
        if self.__readLongClickTriggerThread is not None:
            log("__read_btn_bounce", "清理可能存在的检测键旧长按检测线程")
            self.__readLongClickTriggerThread.cancel()
        # 长按回调不再使能
        self.__readLongClickCallbackEnable = False
        # 关闭光开关
        self.__driveModel.light_switch(False)

    @read_btn_enable
    def read_simulate_btn_bounce(self):
        """
        检测模拟键被弹起
        """
        # 检测模拟键被弹起
        self.__readSimulateBtnIsPress = False
        # 调用弹起流程
        self.__read_btn_bounce()

    @btn_enable
    def __read_long_click_trigger(self):
        """
        检测键长按触发
        """
        # 检测键是按下的状态，长按回调可以使能
        # 这里仅使能，未触发长按回调，因为长按回调是持续性的，将有荧光值更新持续回调
        self.__readLongClickCallbackEnable = self.read_btn_is_press()
        log("__read_long_click_trigger", self.__readLongClickCallbackEnable)

    def mode_btn_is_press(self, log_enable=True):
        """
        模式键是否按下
        :param log_enable: 日志打印使能
        """
        # 模拟按键已经按下
        if self.__modeSimulateBtnIsPress:
            return self.__modeSimulateBtnIsPress

        # 实体按键情况，若不存在实体按键，则返回False
        return self.handle_drive.mode_btn_is_press(log_enable)

    @btn_enable
    def __mode_btn_press(self):
        """
        模式键被按下
        """
        # 移除无用数据
        while len(self.__modeClickQueue) >= MODE_CLICK_QUEUE_SIZE:
            log("移除 modeClickQueue 首个元素，移除前长度", len(self.__modeClickQueue))
            self.__modeClickQueue.pop(0)
        # 操作时间入队
        self.__modeClickQueue.append(time.time())

        if self.__modeLongClickTriggerThread is not None:
            log("__mode_btn_press", "清理可能存在的模式键旧长按检测线程")
            self.__modeLongClickTriggerThread.cancel()

        log("模式键长按探测线程启动")
        # 检测是否在长按
        self.__modeLongClickTriggerThread = threading.Timer(
            LONG_CLICK_TRIGGER_TIME,
            self.__mode_long_click_trigger
        )
        self.__modeLongClickTriggerThread.start()

    @btn_enable
    def mode_simulate_btn_press(self):
        """
        模式模拟键被按下
        """
        self.__modeSimulateBtnIsPress = True
        self.__mode_btn_press()

    @btn_enable
    def __mode_btn_bounce(self):
        """
        模式键弹起
        """
        # 长按检测依旧有效，终止长按检测的线程
        if self.__modeLongClickTriggerThread is not None and self.__modeLongClickTriggerThread.is_alive():
            log("__mode_btn_bounce", "模式键弹起但长按检测依旧有效，终止长按检测线程")
            self.__modeLongClickTriggerThread.cancel()

            # 长按检测依旧有效尚未激活，则属于短按操作
            # 确认是否为双击操作，双击回调激活时才进行回调
            queueSize = len(self.__modeClickQueue)
            if self.__modeDoubleClickCallback is not None \
                and queueSize >= 2 \
                    and self.__modeClickQueue[queueSize - 1] - self.__modeClickQueue[queueSize - 2] < MODE_CONTINUITY_CLICK_INTERVAL:
                log("__modeDoubleClickCallback")
                self.__modeDoubleClickCallback()

    @btn_enable
    def mode_simulate_btn_bounce(self):
        """
        模式模拟键弹起
        """
        self.__modeSimulateBtnIsPress = False
        self.__mode_btn_bounce()

    @btn_enable
    def __mode_long_click_trigger(self):
        """
        模式键长按触发
        """
        # 模式键是按下的状态，可以长按回调
        # 同时，存在长按回调函数
        if self.mode_btn_is_press() and self.__modeLongClickCallback is not None:
            log("__modeLongClickCallback")
            self.__modeLongClickCallback()

    @property
    def button_enable(self):
        return self.__buttonEnable

    def set_button_enable(self, enable):
        """
        修改按钮使能状态
        :param enable: 使能True
        """
        log("button_enable", enable)
        self.__buttonEnable = enable

    def register_read_short_click_callback(self, callback):
        """
        注册检测键短按回调
        :param callback: 回调函数
        """
        log("register_read_short_click_callback", callback)
        self.__readShortClickCallback = callback

    def unbound_read_short_click_callback(self, callback):
        """
        取消绑定检测键短按回调
        :param callback: 被取绑的回调函数，若没有，则不取消绑定
        """
        if self.__readShortClickCallback == callback:
            log("unbound_read_short_click_callback", callback)
            self.__readShortClickCallback = None

    def register_read_long_click_callback(self, callback):
        """
        注册检测键长按回调
        :param callback: 回调函数
        """
        log("register_read_long_click_callback", callback)
        self.__readLongClickCallback = callback

    def unbound_read_long_click_callback(self, callback):
        """
        取消绑定检测键长按回调
        :param callback: 被取绑的回调函数，若没有，则不取消绑定
        """
        if self.__readLongClickCallback == callback:
            log("unbound_read_long_click_callback", callback)
            self.__readLongClickCallback = None

    def register_mode_short_click_callback(self, callback):
        """
        注册模式键短按回调
        :param callback: 回调函数
        """
        log("register_mode_short_click_callback", callback)
        self.__modeShortClickCallback = callback

    def unbound_mode_short_click_callback(self, callback):
        """
        取消绑定模式键短按回调
        :param callback: 被取绑的回调函数，若没有，则不取消绑定
        """
        if self.__modeShortClickCallback == callback:
            log("unbound_mode_short_click_callback", callback)
            self.__modeShortClickCallback = None

    def register_mode_double_click_callback(self, callback):
        """
        注册模式键双击回调
        :param callback: 回调函数
        """
        log("register_mode_double_click_callback", callback)
        self.__modeDoubleClickCallback = callback

    def unbound_mode_double_click_callback(self, callback):
        """
        取消绑定模式键双击回调
        :param callback: 被取绑的回调函数，若没有，则不取消绑定
        """
        if self.__modeDoubleClickCallback == callback:
            log("unbound_mode_double_click_callback", callback)
            self.__modeDoubleClickCallback = None

    def register_mode_long_click_callback(self, callback):
        """
        注册模式键长按回调
        :param callback: 回调函数
        """
        log("register_mode_long_click_callback", callback)
        self.__modeLongClickCallback = callback

    def unbound_mode_long_click_callback(self, callback):
        """
        取消绑定模式键长按回调
        :param callback: 被取绑的回调函数，若没有，则不取消绑定
        """
        if self.__modeLongClickCallback == callback:
            log("unbound_mode_long_click_callback", callback)
            self.__modeLongClickCallback = None

    def read_short_click_thread(self, data_list=None):
        """
        间隔读值的线程
        即短按读值，将读限定次数并计算平均值回调短按函数
        读完后，撤销单击短按状态的锁定，允许其他事件激发

        读完后，如果按键已弹起 或 长按未使能，即不需要长按，可以直接关闭光开关
        否则光开关的关闭动作将托管给该按键的弹起事件处理

        :param data_list: 读到的数据，开始间隔读值时不需要赋值本参数
        """
        # 不是第一次读值，可以直接读取
        # 否则将等间隔时间后才读取
        if data_list is None:
            # 第一次读取，需要等间隔时间后才读取
            # 此次只做数组初始化 和 打开光开关
            log("检测键短按读值线程启动")
            self.__driveModel.light_switch(True)
            data_list = []
        else:
            # 不是第一次读值，可以加入数据
            data_list.append(self.__laserDriveManager.fluorescence)

        log("read_short_click_thread", len(data_list))

        # 已经读到最后一次
        if len(data_list) >= READ_SHORT_CLICK_LIMIT:
            # 均值
            mean = np.mean(data_list)
            log("read short mean", mean)

            # 按键已弹起 或 长按未使能
            if not self.read_btn_is_press() or self.__readLongClickCallback is None:
                # 关闭光开关
                self.__driveModel.light_switch(False)
                # 清理长按检测
                if self.__readLongClickTriggerThread is not None:
                    log("read_short_click_thread", "短按读值结束，检测键已弹起或长按未使能，清理长按检测")
                    self.__readLongClickTriggerThread.cancel()

            # 存在单击回调事件即回调
            if self.__readShortClickCallback is not None:
                self.__readShortClickCallback(mean)

            # 撤销单击短按状态
            self.__readShortPressTime = None
            # 不再循环调用
            return

        # 进行下一轮循环读值
        threading.Timer(
            READ_SHORT_CLICK_INTERVAL,
            self.read_short_click_thread,
            args=(data_list,)).start()

    def register_light_switch_callback(self, callback):
        """
        注册光开关回调
        :param callback: 回调函数
        """
        self.__driveModel.register_light_switch_callback(callback)

    def unbound_light_switch_callback(self, callback):
        """
        取消绑定光开关
        :param callback: 被取绑的回调函数，若没有，则不取消绑定
        """
        self.__driveModel.unbound_light_switch_callback(callback)
