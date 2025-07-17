from Drive.handle.HandleDriveManager import HandleDriveManager
from Drive.laser.LaserDriveManager import LaserDriveManager
from Model.abstract.DriveModelFactory import DriveModelFactory

# 短按读值的时间间隔，单位：秒
SHORT_CLICK_READ_INTERVAL = 0.5


class DriveManager(LaserDriveManager, HandleDriveManager):
    """
    驱动管理器
    单例模式

    本层类似于 Presenter 层
    持有 Model 层 负责驱动相关的逻辑处理，数据交互由Model负责
    """
    def __init__(self):
        self.__driveModel = DriveModelFactory.get_instance(self)
        LaserDriveManager.__init__(self, self.drive_model)
        HandleDriveManager.__init__(self, self.drive_model, self)

    def init_drive(self):
        """
        初始化驱动
        :return: 成功返回None，失败返回错误信息
        """
        # 初始化激光
        laserInitResult = LaserDriveManager._init_drive(self)
        # 初始化失败
        if laserInitResult is not None:
            return laserInitResult

        # 初始化手柄
        handleInitResult = HandleDriveManager._init_drive(self)
        # 初始化失败
        if handleInitResult is not None:
            return handleInitResult

        return None

    @property
    def drive_model(self):
        """
        不应该滥用
        仅在Main模块使用
        """
        return self.__driveModel

    @property
    def apd_status(self):
        """
        apd状态
        :return: apd状态
        """
        return self.__driveModel.apd_status

    @property
    def ni_status(self):
        """
        数据采集卡状态
        :return: 数据采集卡状态
        """
        return self.__driveModel.ni_status

    def get_ni_info(self) -> str:
        """
        获取数据采集卡的信息
        :return: 数据采集卡信息
        """
        return self.__driveModel.get_ni_info()


# 单例，import此属性
driveManager = DriveManager()
