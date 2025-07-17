import clr
from clr import System

from Utils.Log import log
from Utils.Path import rootPath

# dll库位置
HANDLE_DLL = rootPath + "/Drive/handle/dll/ClassLibraryWinIo.dll"

# 地址
# 光开关控制 输出 高电平打开光通道
GPIO_1 = "FED0D018"
# 手柄灯1 里灯远离按键的灯 输出 高电平点亮
GPIO_2 = "FED0D038"
# 光通道打开检测脚 输入 需要手动设为输入口 光通道打开后该脚输入高电平 即光通道打开维持高电平用于判断光开光状态
GPIO_3 = "FED0D048"
# 手柄灯2 外灯靠近按键的灯 输出 高电平点亮
GPIO_4 = "FED0D068"
# 手柄按键1 默认输入 按键按下为低电平（键值为2）；抬起键值为3
GPIO_5 = "FED0D088"
# 面板电源灯控制（变动，未名） 输出 系统启动后输出高电平 未使用
GPIO_6 = "FED0D0A8"
# 手柄按键2 默认输入 按键按下为低电平（键值为2）；抬起键值为3
GPIO_7 = "FED0D0B8"
# 光通道打开指示灯（面板灯） 输出 高电平点亮
GPIO_8 = "FED0D0D8"

# 按键键值
# 按键按下键值
BTN_PRESS_KEY = 2
# 按键抬起键值
BTN_BOUNCE_KEY = 3

# 按键事件
# 按下瞬间
BTN_PRESS_EVENT = 1
# 抬起瞬间
BTN_BOUNCE_EVENT = 2
# 一直按着
BTN_KEEP_PRESS_EVENT = 3

# 按键功能
# 检测键对应的gpio口
READ_BTN_GPIO_NUM = 7
# 模式键对应的gpio口
MODE_BTN_GPIO_NUM = 5

# 设置引脚为输入口的值
INPUT_GPIO = 2
# 输入引脚的电平值
# 开
INPUT_ON_LEVEL = 3
# 关
INPUT_OFF_LEVEL = 2
# 光开光检测脚电平值。因硬件原因，光开关打开时，检测脚为低电平（2）；关闭时，检测脚为高电平（3）
# 开
LIGHT_SWITCH_STATUS_ON_LEVEL = 2
# 关
LIGHT_SWITCH_STATUS_OFF_LEVEL = 3

# 开关的电平值
# 开
ON_LEVEL = 1
# 关
OFF_LEVEL = 0

# C# 方式引入dll库
log("HANDLE_DLL", HANDLE_DLL)
clr.AddReference(HANDLE_DLL)
# 该库命名空间（报错可忽略）
# 切勿将 ClassLibraryWinIo.rar 解压到本项目根目录，否则导入包将会冲突异常
from ClassLibraryWinIo import *


class HandleDrive(object):
    """
    手柄驱动
    实际调用手柄硬件的模块
    """
    def __init__(self):
        # ClassLibraryWinIo 命名空间下的类（报错可忽略）
        self.__ioUtils = ClassWinIo()
        # 按键回调事件
        self.__readPress = None
        self.__readBounce = None
        self.__modePress = None
        self.__modeBounce = None

    def init(self):
        """
        初始化驱动
        HANDLE_DLL 将依赖 WinIo64.dll
        该文件应放置在 Main.py 同级目录下
        """
        # init
        log("HandleDrive init", self.__ioUtils.Init())
        # 注册
        log("register_btn_callback", self.__ioUtils.Interact_With_Python(
            System.Action[System.Object](self.__btn_callback)
        ))
        # 初始化gpio口
        # 设置 GPIO_3 为输入引脚，用于光通道检测
        log("HandleDrive init", "设置 GPIO_3 为 输入引脚")
        self.__set_value(GPIO_3, INPUT_GPIO)
        # 关闭手柄灯
        self.lamp_1_switch(False)
        self.lamp_2_switch(False)
        self.light_lamp_switch(False)
        # 关闭光开关
        self.light_switch(False)
        # 按键抬起
        self.__set_value(GPIO_5, BTN_BOUNCE_KEY)
        self.__set_value(GPIO_7, BTN_BOUNCE_KEY)

    def __get_value(self, gpio):
        """
        获取 gpio value 值

        bit0：电平高低，1：高；0：低
        bit1：输入输出，1：输入；0：输出
        例如：3 -> 11 -> 输入口，高电平
             0 -> 00 -> 输出口，低电平

        :param gpio: gpio口对应的地址
        :return: 取到的值
        """
        return self.__ioUtils.GetValue(int(gpio, 16))

    def __set_value(self, gpio, value):
        """
        设置 gpio value 值

        bit0：电平高低，1：高；0：低
        bit1：输入输出，1：输入；0：输出，可修改gpio的输入输出状态
        例如：3 -> 11 -> 输入口，高电平
             0 -> 00 -> 输出口，低电平

        :param gpio: gpio口对应的地址
        :param value: 需要设置的值
        """
        self.__ioUtils.SetValue(int(gpio, 16), value)

    def register_btn_callback(self, read_press, read_bounce, mode_press, mode_bounce):
        """
        注册手柄按键回调
        :param read_press: 检测键按下
        :param read_bounce: 检测键弹起
        :param mode_press: 模式键按下
        :param mode_bounce: 模式键弹起
        """
        log("register_btn_callback")
        self.__readPress = read_press
        self.__readBounce = read_bounce
        self.__modePress = mode_press
        self.__modeBounce = mode_bounce

    def __btn_callback(self, data):
        """
        按键回调
        :param data: 回调数据，含有GpioNum（gpio_x） 和 GpioEvent（事件）
        """
        # 忽略长按事件
        if data.GpioEvent == BTN_KEEP_PRESS_EVENT:
            return

        log("handle btn callback", "GpioNum: %d; GpioEvent: %d" % (data.GpioNum, data.GpioEvent))
        # 回调
        try:
            if data.GpioNum == READ_BTN_GPIO_NUM:
                # 检测键
                if data.GpioEvent == BTN_PRESS_EVENT and self.__readPress is not None:
                    self.__readPress()
                elif data.GpioEvent == BTN_BOUNCE_EVENT and self.__readBounce is not None:
                    self.__readBounce()

            elif data.GpioNum == MODE_BTN_GPIO_NUM:
                # 模式键
                if data.GpioEvent == BTN_PRESS_EVENT and self.__modePress is not None:
                    self.__modePress()
                elif data.GpioEvent == BTN_BOUNCE_EVENT and self.__modeBounce is not None:
                    self.__modeBounce()

        except BaseException as error:
            log("error __btn_callback 回调注册函数发生异常", str(error))

    def __bool_to_level(self, bool_value):
        """
        将布尔值转为开关控制的电平值
        仅限输出脚
        True: 开，高电平
        False: 关，低电平
        :param bool_value: 布尔值
        :return: 电平值
        """
        if bool_value:
            return ON_LEVEL
        else:
            return OFF_LEVEL

    def light_switch(self, enable):
        """
        光开关控制
        :param enable: 允许光通过：True
        """
        log("light_switch", enable)
        self.__set_value(GPIO_1, self.__bool_to_level(enable))

    def lamp_1_switch(self, enable, log_enable=True):
        """
        手柄灯1的开关
        :param enable: 点亮：True
        :param log_enable: 日志打印使能
        """
        if log_enable:
            log("lamp_1_switch", enable)
        self.__set_value(GPIO_2, self.__bool_to_level(enable))

    def lamp_2_switch(self, enable, log_enable=True):
        """
        手柄灯2的开关
        :param enable: 点亮：True
        :param log_enable: 日志打印使能
        """
        if log_enable:
            log("lamp_2_switch", enable)
        self.__set_value(GPIO_4, self.__bool_to_level(enable))

    def read_btn_is_press(self, log_enable=True):
        """
        检测键是按下状态
        :param log_enable: 日志打印使能
        :return: 是返回True
        """
        value = self.__get_value(GPIO_7) == BTN_PRESS_KEY
        if log_enable:
            log("read_btn_is_press", value)
        return value

    def mode_btn_is_press(self, log_enable=True):
        """
        模式键是按下状态
        :param log_enable: 日志打印使能
        :return: 是返回True
        """
        value = self.__get_value(GPIO_5) == BTN_PRESS_KEY
        if log_enable:
            log("mode_btn_is_press", value)
        return value

    def light_switch_is_on(self):
        """
        光通道（光开关）是否打开
        :return: 已经打开：True
        """
        log("light_switch_is_on get_value", self.__get_value(GPIO_3))
        value = self.__get_value(GPIO_3) == LIGHT_SWITCH_STATUS_ON_LEVEL
        log("light_switch_is_on", value)
        return value

    def light_lamp_switch(self, enable):
        """
        光通道(光开关)指示灯控制
        :param enable: 点亮：True
        """
        log("light_lamp_switch", enable)
        self.__set_value(GPIO_8, self.__bool_to_level(enable))
