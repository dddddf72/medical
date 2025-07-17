import abc

from Model.BaseModel import BaseModel


class ReferentModelAbstract(BaseModel):
    """
    取基准值的Model
    """
    @abc.abstractmethod
    def lamp_open(self):
        """
        打开手柄灯
        """
        pass
