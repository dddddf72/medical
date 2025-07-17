from Model.abstract.CollectModel import CollectModelAbstract
from Utils.Log import log


class CollectModel(CollectModelAbstract):
    def lamp_open(self, log_enable=True):
        if log_enable:
            log("lamp_open")

    def lamp_close(self, log_enable=True):
        if log_enable:
            log("lamp_close")

    def lamp_reverse(self):
        pass
