from Drive.DriveManager import driveManager
from Model.abstract.ReferentModel import ReferentModelAbstract


class ReferentModel(ReferentModelAbstract):
    def lamp_open(self):
        driveManager.handle_drive.lamp_1_switch(True)
        driveManager.handle_drive.lamp_2_switch(False)
