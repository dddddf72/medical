import threading

from PyQt5.QtCore import QTimer

from Config.Config import *
from Drive.DriveManager import driveManager
from Language.language import string_dict
from Presenter.BasePresenter import BasePresenter, GENERATOR_EXEC_DELAY
from Presenter.CollectPresenter import CollectPresenter
from Presenter.ReferentPresenter import ReferentPresenter
from Presenter.SelfCheckPresenter import SelfCheckPresenter
from Utils.Log import log
from View.Factory import MainViewFactory

# 预热时长，单位：分钟
PREHEAT_TIME = config.preheat_time
# 激光功率有效范围
LASER_POWER_MIN = config.laser_power_min
LASER_POWER_MAX = config.laser_power_max
# 检查间隔时间，单位：秒
LASER_CHECK_INTERVAL = config.laser_check_interval
# 稳定检查次数
LASER_STABLE_CHECK_MAX = config.laser_stable_check_max
# 最高重试次数
LASER_CHECK_RETRY_MAX = config.laser_check_retry_max


class MainPresenter(BasePresenter):

    def __init__(self):
        super().__init__()
        # V M 层
        self.__driveModel = driveManager.drive_model
        self.__mainView = None
        # 开机初始化迭代器
        self.__boot_generator = None
        # 激光稳定检查次数
        self.__laserStableSum = 0
        # 激光重试次数
        self.__laserCheckRetrySum = 0
        # 是否正在开机初始化
        self.__isPowerUpInit = False
        # 打开自检界面时需持有其对象，避免被回收
        self.__selfCheckPresenter = None

        # 灯状态，默认关闭，本场景不需要严格把控，因此不和硬件交互获取实际状态
        self.__lampStatus = False
        # 灯闪烁线程
        self.__lampReverseTimer = QTimer(self, timeout=self.__lamp_reverse)

        # 预热成功，功率稳定可进行下一步的标志
        self.__isPreheatSuccess = False
        # 确认了提示的标志，不能移动手柄的提示
        self.__isConfirmTip = False

    @property
    def _view(self):
        return self.__mainView

    def show(self):
        if self.__mainView is None:
            self.__mainView = MainViewFactory.get_instance(self)
        self.__mainView.show()

    def open_referent(self):
        """
        打开取基准值界面，模式键打开
        """
        self.__referentPresenter = ReferentPresenter()
        self.__referentPresenter.show(True)

    def open_self_check(self, is_mode_key_open):
        """
        打开自检界面
        :param is_mode_key_open: 是通过模式键打开
        """
        self.__selfCheckPresenter = SelfCheckPresenter()
        self.__selfCheckPresenter.show(is_mode_key_open)

    def open_collect(self):
        """
        打开采集界面
        仅供debug MainView 使用
        """
        self.__collectPresenter = CollectPresenter()
        self.__collectPresenter.show()

    def power_up_init(self):
        """
        开机初始化
        """
        # 正在开机初始化，不允许重复操作
        if self.__isPowerUpInit:
            log("还在初始化中，不得重复操作")
            self.__mainView.error("还在初始化中，不得重复操作")
            return

        # 开始初始化
        log("start_power_up_init")
        self.__isPowerUpInit = True
        # 提示不得移动手柄
        self.__mainView.need_confirm_tip(string_dict("dontMoveHandle"))

        # 获取迭代器
        self.__boot_generator = self.__power_up_init_generator()
        # 启动
        next(self.__boot_generator)
        # 回传生成器以便执行下一步
        self.__boot_generator.send(self.__boot_generator)

    def __power_up_init_generator(self):
        """
        开机初始化的生成器
        实现开机初始化流程

        :return: 生成器
        """

        # 等待生成器回传
        generator = yield

        # 初始化驱动
        initDriveError = driveManager.init_drive()
        if initDriveError is not None:
            # 初始化失败
            self.__mainView.init_drive_error(initDriveError)
            self.__isPowerUpInit = False
            yield

        # 锁定手柄
        driveManager.set_button_enable(False)

        # 手柄灯闪烁
        self.__lampReverseTimer.start(200)

        # 预热
        # 预热结束回调 preheat_end 时将回归本流程继续执行
        self.__mainView.start_preheat(PREHEAT_TIME)
        yield

        # 检查激光功率
        # 初始化数据
        self.__laserStableSum = 0
        self.__laserCheckRetrySum = 0
        # 延时调用，确保laserStatus = yield 在函数调用前执行，避免generator正在运行中的错误
        threading.Timer(
            GENERATOR_EXEC_DELAY,
            self.__laser_power_check,
            args=(generator,)).start()

        # 等待激光功率检查结果，稳定为True，不稳定为False
        laserStatus = yield
        if laserStatus:
            # 功率稳定，记录状态
            self.__isPreheatSuccess = True
            # 是否确认提示，未确认需等待确认，由 confirm_tip next()
            if not self.__isConfirmTip:
                log("还未确认提示，等待确认")
                yield

            # 稳定后操作
            self.__laser_power_stable()

        else:
            # 不稳定
            self.__laser_power_instability()

    def __laser_power_check(self, generator):
        """
        激光功率检查
        周期任务

        :param generator: 生成器，用于进行下一步

        策略：
        每隔一定时间检查一次
        若功率不符合规则，清空合规次数，开始下一轮检查
            若已达失败重试次数上限，生成器返回False
        若功率符合规则，更新当前合规次数，开始下一轮检查
            当合规次数已达要求，生成器返回True

        回调：
        检查进度：_laser_power_check_progress
        """
        log("__laser_power_check")
        # 检查激光功率稳定性
        self.__laserCheckRetrySum += 1
        laserPower = self.__driveModel.get_laser_power()
        if LASER_POWER_MIN <= laserPower <= LASER_POWER_MAX:
            # 符合规则
            self.__laserStableSum += 1
        else:
            # 不符合规则
            self.__laserStableSum = 0

        # 界面更新
        self.__laser_power_check_progress()

        # 根据设计，满足条件时迭代将在此结束
        try:
            # 已达稳定检查次数上限
            if self.__laserStableSum >= LASER_STABLE_CHECK_MAX:
                generator.send(True)
                return

            # 已达最高重试次数上限
            if self.__laserCheckRetrySum >= LASER_CHECK_RETRY_MAX:
                generator.send(False)
                return

        except StopIteration:
            # 功率检查结束，不再执行后续步骤
            log("laser_power_check", "StopIteration")
            return

        # 开始定时任务
        log("开启激光检测定时任务")
        threading.Timer(LASER_CHECK_INTERVAL, self.__laser_power_check, args=(generator,)).start()

    def __laser_power_check_progress(self):
        """
        激光功率检查进度
        """
        log("激光功率检查进度", "稳定次数：%d / %d 重试次数：%d / %d"
                        % (
                            self.__laserStableSum,
                            LASER_STABLE_CHECK_MAX,
                            self.__laserCheckRetrySum,
                            LASER_CHECK_RETRY_MAX
                        )
            )
        self.__mainView.laser_power_check_progress(
            self.__laserStableSum,
            LASER_STABLE_CHECK_MAX,
            self.__laserCheckRetrySum,
            LASER_CHECK_RETRY_MAX
        )

    def __laser_power_stable(self):
        """
        激光功率稳定
        """
        log("__laser_power_stable")
        # 停止手柄闪烁控制
        self.__lampReverseTimer.stop()

        # 功率稳定进入下一步
        self.__isPowerUpInit = False
        self.__mainView.laser_power_stable()
        self.__mainView.open_self_check(False)

    def __laser_power_instability(self):
        """
        激光功率不稳定
        """
        log("__laser_power_instability")
        self.__isPowerUpInit = False
        self.__mainView.laser_power_instability()

    def preheat_end(self):
        """
        预热结束
        回归 __power_up_init_generator 的开机初始化流程
        """
        log("preheat_end")
        next(self.__boot_generator)

    def __lamp_reverse(self):
        """
        手柄灯闪烁，lamp_1_switch 常亮； lamp_2_switch 闪烁
        """
        if self.__lampStatus:
            self.__driveModel.lamp_switch(True, True)
        else:
            self.__driveModel.lamp_switch(False, True)
        self.__lampStatus = not self.__lampStatus

    def confirm_tip(self):
        """
        确认提示
        不得移动手柄的提示
        """
        log("确认提示")
        self.__isConfirmTip = True
        # 如果已经预热成功，需要回到开机初始化流程
        if self.__isPreheatSuccess:
            log("之前已经预热成功，可进行下一步")
            try:
                next(self.__boot_generator)
            except StopIteration:
                log("confirm_tip", "StopIteration")
