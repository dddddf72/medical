from Model.abstract.ReferentModel import ReferentModelAbstract
from Utils.Log import log


class ReferentModel(ReferentModelAbstract):
    def lamp_open(self):
        log("lamp_open")
