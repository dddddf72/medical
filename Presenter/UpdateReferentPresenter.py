from Presenter.ReferentPresenter import ReferentPresenter
from Utils.SurgicalData import surgicalData


class UpdateReferentPresenter(ReferentPresenter):
    """
    更新基准值
    """

    def __init__(self, referent_list):
        """
        :param referent_list: 基准值列表
        """
        super().__init__(referent_list)

    def show(self, is_mode_key_open=True):
        """
        :param is_mode_key_open: 更新取基准值，本参数必须为True
        """
        super(UpdateReferentPresenter, self).show(True)
        # 手术记录备注
        surgicalData.add_remark("update referent")
        # 显示滚动条
        self._view.scroll_bar_show(True)

    def _mode_long_click(self):
        """
        重写 模式键长按
        TODO MS 22.3.28 长按打开取值界面，此代码为模式键临时代码，该功能尚未完善
        """
        # 打开取值界面
        self._view.open_collect()
