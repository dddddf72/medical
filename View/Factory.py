import abc

import View.debug.collect.CollectView
import View.debug.main.MainView
import View.debug.referent.ReferentView
import View.debug.self_check.SelfCheckView
import View.release.collect.CollectView
import View.release.main.MainView
import View.release.referent.ReferentView
import View.release.self_check.SelfCheckView
from Config.Config import config
from Utils.Log import log


class BaseViewFactory(metaclass=abc.ABCMeta):
    """
    界面类的基础工厂，所有工厂继承本类使用
    """
    @staticmethod
    @abc.abstractmethod
    def get_instance(presenter):
        """
        获取实例
        :param presenter: P层
        :return: V层
        """
        pass


class MainViewFactory(BaseViewFactory):
    """
    主界面工厂
    """
    @staticmethod
    def get_instance(presenter):
        if config.view_is_debug or config.model_is_debug:
        # if config.view_is_debug:
            log("MainViewFactory", "V or M 为 debug MainView使用debug")
            return View.debug.main.MainView.MainView(presenter)
        else:
            return View.release.main.MainView.MainView(presenter)


class SelfCheckViewFactory(BaseViewFactory):
    """
    自检界面工厂
    """
    @staticmethod
    def get_instance(presenter):
        if config.view_is_debug:
            return View.debug.self_check.SelfCheckView.SelfCheckView(presenter)
        else:
            return View.release.self_check.SelfCheckView.SelfCheckView(presenter)


class ReferentViewFactory(BaseViewFactory):
    """
    自检界面工厂
    """
    @staticmethod
    def get_instance(presenter):
        if config.view_is_debug:
            return View.debug.referent.ReferentView.ReferentView(presenter)
        else:
            return View.release.referent.ReferentView.ReferentView(presenter)


class CollectViewFactory(BaseViewFactory):
    """
    检测采集的界面工厂
    """
    @staticmethod
    def get_instance(presenter, *args):
        if config.view_is_debug:
            return View.debug.collect.CollectView.CollectView(presenter, args[0])
        else:
            return View.release.collect.CollectView.CollectView(presenter, args[0])
