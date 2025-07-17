import time

from Config.Config import config
from Drive.DriveManager import driveManager
from Drive.laser.LaserDrive import LaserDrive
from Model.abstract.SelfCheckModel import SelfCheckModelAbstract
from Utils.Log import log


class SelfCheckModel(SelfCheckModelAbstract):
    def __init__(self, presenter):
        super().__init__(presenter)
        # 灯状态，默认关闭，本场景不需要严格把控，因此不和硬件交互获取实际状态
        self.lampStatus = False

    def ni_status(self):
        return driveManager.ni_status

    def rfid_read_preset_value(self, generator=None):
        log("rfid_read_preset_value", 0.5)
        if generator is None:
            return 0.5
        else:
            generator.send(0.5)

    def laser_device_status(self):
        # 固件原因无法获取有效状态，以电压值进行衡量
        # 将电压值映射到功率值
        power = LaserDrive.voltage_to_power(driveManager.laser_drive.get_voltage())
        return config.laser_power_min <= power <= config.laser_power_max

    def light_switch_status(self):
        """
        光开关状态

        控制与检查错开50毫秒是为了避免电压不稳造成的检查异常

        总耗时150毫秒，不会影响到界面，所以不使用异步处理
        """
        # 打开光开关
        driveManager.handle_drive.light_switch(True)
        time.sleep(0.05)
        # 检查状态
        open_status = driveManager.handle_drive.light_switch_is_on()
        time.sleep(0.05)
        # 关闭光开关
        driveManager.handle_drive.light_switch(False)
        time.sleep(0.05)
        # 检查状态
        close_status = driveManager.handle_drive.light_switch_is_on()

        # 打开时是True 关闭时是False 则 光开关正常
        return open_status and not close_status

    def apd_status(self):
        return driveManager.apd_status

    def lamp_reverse(self):
        if self.lampStatus:
            driveManager.handle_drive.lamp_1_switch(True, False)
            driveManager.handle_drive.lamp_2_switch(True, False)
        else:
            driveManager.handle_drive.lamp_1_switch(True, False)
            driveManager.handle_drive.lamp_2_switch(False, False)
        self.lampStatus = not self.lampStatus
