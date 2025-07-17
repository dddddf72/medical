from Language.language import string_dict, operate_dict
from Utils.DeviceUtil import shut
from View.BaseView import main_thread
from View.abstract.ReferentView import ReferentViewAbstract
from View.custom_widget.MsgBoxDialog import MsgBoxDialog
from View.custom_widget.SettingsDialog import SettingsDialog
from View.release.ReleaseBaseView import ReleaseBaseView
from View.release.referent.referent import Ui_MainWindow


class ReferentView(ReferentViewAbstract, Ui_MainWindow, ReleaseBaseView):
    """
    取基准值：有限定个预留位置
    补值：超过限定时列表最下面会空出一个表明可以继续采集
    """
    def __init__(self, presenter):
        # 测量值的 item 数组
        self.__widgetList = []
        super().__init__(presenter)

    def _init_ui(self):
        # 后门使能
        self.back_door_enable()
        # 关机
        self.button_shut.clicked.connect(self.__shut)
        # 帮助
        self.button_help.clicked.connect(self.__help)

        # 初始化测量值空位
        for index in range(self.presenter.tries_limit):
            self.__widgetList.append(self._add_item(index + 1, ""))

        # 填充已有测量值，此场景仅在补值操作时出现，即测量值不限
        for index, referent in enumerate(self.presenter.referent_list):
            self.reference_value_progress(referent, index + 1, -1)

        # 直接滚动到末尾
        self.listWidget.scrollToBottom()

    @main_thread
    def error(self, msg):
        self.label_warn.setStyleSheet(self.label_warn_style("255,255,0"))
        self.show_tip(msg)

    @main_thread
    def tip(self, msg):
        self.label_warn.setStyleSheet(self.label_warn_style("180,180,180"))
        self.show_tip(msg)

    @main_thread
    def reference_value_progress(self, reference_value, times, tries_limit):
        # 提示取下一个基准值
        self.tip(string_dict("nextReferentValue"))

        # 更新基准值
        self.formatFinalValue(self._value_to_text(max(self.presenter.referent_list)))

        # 修改
        self.__widgetList[times - 1].update_label(self._value_to_text(reference_value))

        # 当前取值已经大于限制数量（即补值操作） 并且 没有空的控件提示可输入
        if times > tries_limit and times >= len(self.__widgetList):
            # 新增测量值
            self.__widgetList.append(self._add_item(len(self.__widgetList) + 1, ""))

        # 滚动
        self._scrollTimer.start()

    @main_thread
    def scroll_bar_show(self, show_enable):
        self._scroll_bar_show(show_enable)

    def show_tip(self, msg):
        """
        显示提示信息
        :param msg: 提示信息
        """
        self.label_warn.setText(msg)

    def __shut(self):
        """
        关机
        """
        # 弹框提示
        self.shutDialog = MsgBoxDialog(
            string_dict("shutTip"),
            string_dict("shutMsg"),
            operate_dict("shut"), shut,
            operate_dict("cancel"), None
        )
        self.shutDialog.show()

    def __help(self):
        """
        帮助
        """
        self.settingsDialog = SettingsDialog()
        self.settingsDialog.show()
