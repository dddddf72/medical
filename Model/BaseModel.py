import abc


class BaseModel(metaclass=abc.ABCMeta):
    """
    Model 层的基础抽象类，所有Model继承本类实现
    """

    def __init__(self, presenter):
        """
        需设置持有本M的P层
        """
        super().__init__()
        self.presenter = presenter
