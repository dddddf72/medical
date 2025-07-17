from Model.abstract.SelfCheckModel import SelfCheckModelAbstract
from Utils.Log import log


class SelfCheckModel(SelfCheckModelAbstract):
    def ni_status(self):
        log("ni_status", False)
        return False

    def rfid_read_preset_value(self, generator=None):
        log("rfid_read_preset_value", 0.5)
        if generator is None:
            return 0.5
        else:
            generator.send(0.5)

    def laser_device_status(self):
        log("laser_device_status", False)
        return False

    def light_switch_status(self):
        log("light_switch_status", False)
        return False

    def apd_status(self):
        log("apd_status", False)
        return False

    def lamp_reverse(self):
        # log("lamp_reverse")
        pass
