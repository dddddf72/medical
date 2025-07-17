from PyQt5.QtCore import QTimer

from Config.Config import *
from Drive.DriveManager import driveManager
from Language.language import string_dict
from Model.Factory import ReferentModelFactory
from Presenter.BasePresenter import BasePresenter
from Presenter.CollectPresenter import CollectPresenter
from Utils.Log import log
from Utils.SurgicalData import surgicalData
from View.Factory import ReferentViewFactory

# 基准值的最小值
REFERENT_MIN = config.referent_min
# 基准值的最大值
REFERENT_MAX = config.referent_max
# 取基准值的次数
TRIES_LIMIT = config.tries_limit


class ReferentPresenter(BasePresenter):
    def __init__(self, referent_list=None):
        super().__init__()
        # 是否为模式键打开的本界面
        self.__isModeKeyOpen = False
        # 打开采集界面时需持有其对象，避免被回收
        self.__collectPresenter = None

        # 基准值列表（只能增加不能删改）
        log("referent_list", referent_list)
        self._referentList = referent_list
        if self._referentList is None:
            self._referentList = []

        # V M 层
        self.__referentModel = ReferentModelFactory.get_instance(self)
        self.__referentView = ReferentViewFactory.get_instance(self)

    @property
    def _view(self):
        return self.__referentView

    def show(self, is_mode_key_open=False):
        """
        显示
        :param is_mode_key_open: 通过模式键打开的，需要使用 UpdateReferentPresenter 才能激活所需功能
        """
        super(ReferentPresenter, self).show()
        # 注册手柄短按事件
        driveManager.register_read_short_click_callback(self.confirm_referent)
        # 注册光开关回调
        driveManager.register_light_switch_callback(self.__light_switch_callback)
        # 解除手柄锁定
        driveManager.set_button_enable(True)
        # 点亮手柄灯
        self.__referentModel.lamp_open()
        # 新增手术记录
        surgicalData.insert_surgical()

        # 界面显示
        self.__isModeKeyOpen = is_mode_key_open
        self.__referentView.show()

    def _close(self):
        super(ReferentPresenter, self)._close()
        # 取绑回调事件
        driveManager.unbound_read_short_click_callback(self.confirm_referent)
        driveManager.unbound_light_switch_callback(self.__light_switch_callback)
        # 回收
        self.__referentModel = None
        self.__referentView.close()
        self.__referentView = None

    def get_referent_model_test(self):
        """
        获取自检model层
        仅限测试时使用，不得在生产中使用
        :return: self_check_model
        """
        return self.__referentModel

    def get_is_mode_key_open(self):
        return self.__isModeKeyOpen

    @property
    def referent_min(self):
        return REFERENT_MIN

    @property
    def referent_max(self):
        return REFERENT_MAX

    @property
    def tries_limit(self):
        return TRIES_LIMIT

    @property
    def referent_list(self):
        return self._referentList

    def open_collect(self):
        """
        打开采集界面
        """
        # 延时关闭本界面
        QTimer(self).singleShot(1000, self._close)
        # 打开采集界面
        self.__collectPresenter = CollectPresenter(self._referentList)
        self.__collectPresenter.show()

    def __light_switch_callback(self, enable):
        """
        光开关控制的回调函数
        :param enable: 允许光通过：True
        """
        self.__referentView.light_switch_callback(enable)

    def confirm_referent(self, value):
        """
        确认基准值
        :param value: 基准值
        """
        log("confirm_referent", value)

        # 不是模式键进入 并且 基准值已达限制次数时，不进行后续操作
        if not self.__isModeKeyOpen and len(self._referentList) >= TRIES_LIMIT:
            log("confirm_referent error", "非模式键取基准值，基准值数量已超过限额，丢弃")
            return

        # 合规性检查
        if REFERENT_MIN <= value <= REFERENT_MAX:
            # 合规
            pass

        else:
            # 不合规
            log("referent", "该基准值不符合规则")
            self.__referentView.error(string_dict("referentValueError") + str(format(value, ".3f")))
            return

        # 限制取基准值的次数
        triesLimit = TRIES_LIMIT
        if self.__isModeKeyOpen:
            triesLimit = -1

        # 合规操作，进度管理
        self._referentList.append(value)
        log("确认基准值进度", "基准值：%s; 进度: %d / %d"
            % (str(value), len(self._referentList), triesLimit)
            )
        self.__referentView.reference_value_progress(
            value,
            len(self._referentList),
            triesLimit
        )

        # 保存到文件
        surgicalData.save_referent(value)

        # 模式键进入的不做后续处理
        if self.__isModeKeyOpen:
            return

        # 已达基准值限制次数
        if len(self._referentList) >= triesLimit:
            log("已达基准值限制次数")
            # 打开检测界面
            self.__referentView.open_collect()

    def _mode_long_click(self):
        """
        重写 模式键长按
        取基准值时不允许模式键长按回调
        补值 UpdateReferentPresenter 允许
        TODO MS 22.5.20 长按管理，此代码为模式键临时代码，该功能尚未完善
        """
        log("_mode_long_click", "采集数量不足，不得跳转")
        self.__referentView.error(string_dict("nextReferentValue"))
