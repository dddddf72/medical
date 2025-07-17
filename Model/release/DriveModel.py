from Drive.laser.LaserDrive import get_laser_power
from Drive.laser.NiDataAcqThread import NiDataAcqThread
from Model.abstract.DriveModel import DriveModelAbstract
from Utils.Log import log


class DriveModel(DriveModelAbstract):

    def __init__(self, presenter):
        super().__init__(presenter)
        # 数据采集线程
        self.__niDataAcqThread = None

    def get_ni_info(self) -> str:
        if self.__niDataAcqThread is not None:
            return self.__niDataAcqThread.get_ni_info()
        else:
            return "get_ni_info error"

    def light_switch(self, enable):
        super(DriveModel, self).light_switch(enable)
        from Drive.DriveManager import driveManager
        # 光开关指示灯控制
        driveManager.handle_drive.light_lamp_switch(enable)
        # 硬件光开关控制
        return driveManager.handle_drive.light_switch(enable)

    def start_up_laser(self):
        log("start_up_laser")
        from Drive.DriveManager import driveManager
        # 打开设备
        if not driveManager.laser_drive.open_device():
            # 打开失败
            return False

        # 使能设备
        if not driveManager.laser_drive.set_enable(True):
            # 使能失败
            return False

        # 设置功率
        return driveManager.laser_drive.set_power(get_laser_power())

    def get_laser_power(self):
        from Drive.DriveManager import driveManager
        return driveManager.laser_drive.get_power()

    def start_acq(self, slot):
        # 已打开
        if self.__niDataAcqThread is not None:
            return

        # 创建线程
        self.__niDataAcqThread = NiDataAcqThread(slot)
        # 开始采集
        self.__niDataAcqThread.start()

    @property
    def apd_status(self):
        """
        apd状态
        本状态需要在预热结束后获取
        :return: apd状态
        """
        return self.__niDataAcqThread.apd_status

    @property
    def ni_status(self):
        """
        本状态需要在激光发生器正常打开，数据采集线程初始化运行 之后获取
        """
        return self.__niDataAcqThread.ni_status

    def lamp_switch(self, lamp_1, lamp_2):
        from Drive.DriveManager import driveManager
        driveManager.handle_drive.lamp_1_switch(lamp_1, False)
        driveManager.handle_drive.lamp_2_switch(lamp_2, False)
