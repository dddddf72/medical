from Drive.laser.LaserDrive import LaserDrive
from Language.language import string_dict
from Utils.Log import log


class LaserDriveManager(object):
    """
    激光驱动管理器
    """
    def __init__(self, drive_model):
        self.__driveModel = drive_model
        # 驱动
        self.__laserDrive = LaserDrive()
        # 是否已成功初始化的标志
        self.__initResult = False
        # 荧光值，最新数据
        self.__fluorescence = 0
        # 荧光值更新的回调函数
        self.__fluorescenceCallback = None

    def _init_drive(self):
        """
        初始化激光
        :return: 成功返回None，失败返回错误信息
        """
        # 驱动已初始化
        if self.__initResult:
            return None

        # 启动激光发射器
        if not self.__driveModel.start_up_laser():
            # 启动失败
            log(string_dict("startUpLaserError"))
            return string_dict("startUpLaserError")

        # 启动数据采集
        self.__driveModel.start_acq(self.__acq_slot)

        # 初始化成功
        self.__initResult = True
        return None

    def __acq_slot(self, data):
        """
        数据采集的槽函数
        :param data: 荧光值电压
        """
        self.__fluorescence = data
        if self.__fluorescenceCallback is not None:
            self.__fluorescenceCallback(data)

    def register_fluorescence_callback(self, callback):
        """
        注册荧光值更新的回调
        :param callback: 回调函数
        """
        log("register_fluorescence_callback", callback)
        self.__fluorescenceCallback = callback

    @property
    def fluorescence(self):
        """
        荧光值
        """
        return self.__fluorescence

    @property
    def laser_drive(self):
        return self.__laserDrive
