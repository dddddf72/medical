from PyQt5.QtCore import QTimer

from Config.Config import *
from Drive.DriveManager import driveManager
from Model.Factory import CollectModelFactory
from Presenter.BasePresenter import BasePresenter
from Utils.SoundUtil import SoundUtil, BEEP_MP3, DI_MP3
from Utils.SurgicalData import surgicalData
from View.Factory import CollectViewFactory

# 通过基准值得到阈值的倍数（大于1）
MULTIPLE_THRESHOLD = config.multiple_threshold

# 瞬间播放的时长，单位：秒，（当前被用于长按 和 修改音量的提示）
PLAY_SECOND_TIME = 1
# 短按触发警告的播放时长，单位：秒
SHORT_WARN_TIME = config.play_time


class CollectPresenter(BasePresenter):
    def __init__(self, referent_list=None):
        # V M 层
        super().__init__()

        # 基准值列表，由取基准值流程提供
        if referent_list is None:
            referent_list = []
        self.__referentList = referent_list

        # 基准值，不得为0，最小只能是一个接近0的数
        referent_value = 0.001
        if len(self.__referentList) > 0:
            referent_value = max(referent_list)
        else:
            log("error", "基准值列表为空，但基准值不得为0，修改为0.001")
        # 不得太小
        if referent_value < 1e-3:
            log("error", "基准值小于0.001，但基准值不得为0 或 过小，修改为0.001")
            referent_value = 0.001

        # 阈值
        self.__threshold = referent_value * MULTIPLE_THRESHOLD

        # 各层
        self.__collectModel = CollectModelFactory.get_instance(self)
        self.__collectView = CollectViewFactory.get_instance(self, referent_value)
        # 提示声工具
        self.__beepUtil = SoundUtil(BEEP_MP3, PLAY_SECOND_TIME)
        self.__shortBeepUtil = SoundUtil(BEEP_MP3, SHORT_WARN_TIME)
        # 连台手术打开的取基准值界面
        self.__referentPresenter = None

    @property
    def _view(self):
        return self.__collectView

    def show(self):
        super(CollectPresenter, self).show()

        # 注册手柄事件
        driveManager.register_read_short_click_callback(self.__fluorescence_update)

        # 长按功能
        if config.read_long:
            driveManager.register_read_long_click_callback(self.__read_long_click)

        # 注册光开关回调
        driveManager.register_light_switch_callback(self.__light_switch_callback)
        # 点亮手柄灯
        self.__collectModel.lamp_open()

        # 界面显示
        self.__collectView.show()

    def _close(self):
        super(CollectPresenter, self)._close()
        # 取绑回调事件
        driveManager.unbound_read_short_click_callback(self.__fluorescence_update)
        driveManager.unbound_read_long_click_callback(self.__read_long_click)
        driveManager.unbound_light_switch_callback(self.__light_switch_callback)
        driveManager.unbound_mode_double_click_callback(self.install_complete_mode_click)
        # 回收
        self.__collectModel = None
        self.__collectView.close()
        self.__collectView = None

    def __read_long_click(self, data):
        """
        检测键长按事件
        :param data: 荧光值
        """
        # 更改手柄灯状态，实现闪烁效果
        self.__collectModel.lamp_reverse()

        # 大于阈值，警告
        if data > self.__threshold:
            self.__beepUtil.play_second()
        # 更新
        self.__fluorescence_update(data, False)

    def __fluorescence_update(self, data, play_enable=True):
        """
        荧光值更新时的回调
        当前用于短按回调
        :param data: 荧光值
        :param play_enable: 警告播放使能
        """
        # 大于阈值
        if data > self.__threshold:
            # 保存
            surgicalData.save_warn(data)
            # 警告
            if play_enable:
                self.__shortBeepUtil.play_second()
        # 界面刷新
        self.__collectView.refresh_value(data)

    def __light_switch_callback(self, enable):
        """
        光开关控制的回调函数
        :param enable: 允许光通过：True
        """
        # 关闭光开关时需要点亮手柄灯，恢复初始化时灯常亮的状态
        if not enable:
            self.__collectModel.lamp_open()
        # 界面状态
        self.__collectView.light_switch_callback(enable)

    @property
    def multiple_threshold(self):
        return MULTIPLE_THRESHOLD

    def install_complete(self):
        """
        无菌护套装配完成
        进入取基准值界面
        该由UI线程调用
        """
        # 关手柄灯
        self.__collectModel.lamp_close()

        # 延时关闭本界面
        QTimer(self).singleShot(1000, self._close)

        # 基准值界面已经引用了采集界面，故延时引用
        from Presenter.ReferentPresenter import ReferentPresenter
        self.__referentPresenter = ReferentPresenter()
        self.__referentPresenter.show()

    def set_volume(self, volume):
        """
        设置音量
        :param volume: 音量
        """
        # 范围管理
        if volume < 0:
            volume = 0
        if volume > 1:
            volume = 1

        # 保存配置
        config.set_volume(volume)
        # 修改当前声音
        SoundUtil.set_volume(volume)
        # 播放
        SoundUtil(DI_MP3, PLAY_SECOND_TIME).play_second()

    def install_complete_mode_click(self):
        """
        通过模式键点击实现装配完成的确定
        """
        log("install_complete_mode_click")
        # 仅允许回调一次
        driveManager.unbound_mode_double_click_callback(self.install_complete_mode_click)
        # 关闭dialog
        self.__collectView.close_dialog()
        # 装配完成
        self.install_complete()

    def _mode_long_click(self):
        """
        重写 模式键长按
        TODO MS 22.3.28 当前模式键长按将直接打开取基准值界面
        """
        # 模式键选择
        self._view.mode_choice(self.__referentList)
