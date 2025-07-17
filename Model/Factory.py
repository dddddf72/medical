import abc

import Model.debug.CollectModel
import Model.debug.ReferentModel
import Model.debug.SelfCheckModel
import Model.release.CollectModel
import Model.release.ReferentModel
import Model.release.SelfCheckModel
from Config.Config import config


class BaseModelFactory(metaclass=abc.ABCMeta):
    """
    Model的基础工厂，所有工厂继承本类使用
    """
    @staticmethod
    @abc.abstractmethod
    def get_instance(presenter):
        """
        获取实例
        :param presenter: P层
        :return: M层
        """
        pass


class SelfCheckModelFactory(BaseModelFactory):
    """
    自检Model工厂
    """
    @staticmethod
    def get_instance(presenter):
        if config.model_is_debug:
            return Model.debug.SelfCheckModel.SelfCheckModel(presenter)
        else:
            return Model.release.SelfCheckModel.SelfCheckModel(presenter)


class ReferentModelFactory(BaseModelFactory):
    """
    取基准值的Model工厂
    """
    @staticmethod
    def get_instance(presenter):
        if config.model_is_debug:
            return Model.debug.ReferentModel.ReferentModel(presenter)
        else:
            return Model.release.ReferentModel.ReferentModel(presenter)


class CollectModelFactory(BaseModelFactory):
    """
    检测采集的Model工厂
    """
    @staticmethod
    def get_instance(presenter):
        if config.model_is_debug:
            return Model.debug.CollectModel.CollectModel(presenter)
        else:
            return Model.release.CollectModel.CollectModel(presenter)
