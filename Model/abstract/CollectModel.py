import abc

from Model.BaseModel import BaseModel


class CollectModelAbstract(BaseModel):
    """
    检测采集界面的Model
    """
    @abc.abstractmethod
    def lamp_open(self, log_enable=True):
        """
        打开手柄灯
        :param log_enable: 日志打印使能
        """
        pass

    @abc.abstractmethod
    def lamp_close(self, log_enable=True):
        """
        关闭手柄灯
        :param log_enable: 日志打印使能
        """
        pass

    @abc.abstractmethod
    def lamp_reverse(self):
        """
        手柄灯取反，点亮的改为熄灭，熄灭的改为点亮
        """
        pass
