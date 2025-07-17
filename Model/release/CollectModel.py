from Drive.DriveManager import driveManager
from Model.abstract.CollectModel import CollectModelAbstract


class CollectModel(CollectModelAbstract):
    def __init__(self, presenter):
        super().__init__(presenter)
        # 灯状态，默认关闭，本场景不需要严格把控，因此不和硬件交互获取实际状态
        self.lampStatus = False

    def lamp_open(self, log_enable=True):
        driveManager.handle_drive.lamp_1_switch(True, log_enable)
        driveManager.handle_drive.lamp_2_switch(True, log_enable)

    def lamp_close(self, log_enable=True):
        driveManager.handle_drive.lamp_1_switch(False, log_enable)
        driveManager.handle_drive.lamp_2_switch(False, log_enable)

    def lamp_reverse(self):
        if self.lampStatus:
            self.lamp_open(False)
        else:
            self.lamp_close(False)
        self.lampStatus = not self.lampStatus
