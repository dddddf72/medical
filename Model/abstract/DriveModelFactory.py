import Model.debug.DriveModel
import Model.release.DriveModel
from Config.Config import config


class DriveModelFactory(object):
    """
    驱动的Model工厂
    驱动的工厂类不放入工厂文件，避免循环引用
    """
    @staticmethod
    def get_instance(presenter):
        if config.model_is_debug:
            return Model.debug.DriveModel.DriveModel(presenter)
        else:
            return Model.release.DriveModel.DriveModel(presenter)
