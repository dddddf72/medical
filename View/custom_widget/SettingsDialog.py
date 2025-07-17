import sys

from PyQt5 import QtCore, QtWidgets
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QPixmap
from PyQt5.QtWidgets import QMainWindow, QWidget, QApplication

from Config.Config import FIRMWARE, SOFTWARE
from Language.language import string_dict, operate_dict
from Utils.DeviceUtil import shut
from Utils.Path import rootPath
from Utils.ResolutionTools import scaleSizeW, scaleSizeH, setDesktop
from View.custom_widget.MsgBoxDialog import MsgBoxDialog
from View.custom_widget.SetDateTime import SetDateTime

# 图片所在路径
imgPath = rootPath + "/View/img"


class SettingsDialog(QMainWindow):
    """
    装配提示
    """
    def __init__(self):
        super(SettingsDialog, self).__init__()
        # 界面
        self.setupUi(self)

    def setupUi(self, MainWindow):
        MainWindow.setObjectName("MainWindow")
        MainWindow.resize(scaleSizeW(430), scaleSizeH(300))
        # 无边框
        MainWindow.setWindowFlags(Qt.FramelessWindowHint)
        # 布局
        self.centralwidget = QWidget(MainWindow)
        self.centralwidget.setObjectName(u"centralwidget")

        # 背景图
        self.label_bg = QtWidgets.QLabel(self.centralwidget)
        self.label_bg.setScaledContents(True)
        self.label_bg.setPixmap(QPixmap(imgPath + "/common/bg_settings.png"))
        self.label_bg.setGeometry(QtCore.QRect(scaleSizeW(0), scaleSizeH(0), scaleSizeW(430), scaleSizeH(300)))
        self.label_bg.setObjectName("label_bg")

        # 关机
        self.button_shut = QtWidgets.QPushButton(self.centralwidget)
        self.button_shut.setObjectName("button_shut")
        self.button_shut.setGeometry(QtCore.QRect(scaleSizeW(50), scaleSizeH(25), scaleSizeW(130), scaleSizeH(50)))
        self.button_shut.setStyleSheet(
            "QPushButton#button_shut{"
            "border-image: url(" + imgPath + "/common/shut.png);}")
        self.button_shut.clicked.connect(self.__shut)

        # 固件号
        # self.label_firmware = QtWidgets.QLabel(self.centralwidget)
        # self.label_firmware.setObjectName("label_firmware")
        # self.label_firmware.setText("固件号：" + FIRMWARE)
        # self.label_firmware.setGeometry(QtCore.QRect(scaleSizeW(50), scaleSizeH(105), scaleSizeW(400), scaleSizeH(40)))
        # self.label_firmware.setStyleSheet(
        #     "QLabel#label_firmware{"
        #     "font-size: 22px;"
        #     "color: rgb(255,255,255)}"
        # )

        # 软件版本号
        self.label_software = QtWidgets.QLabel(self.centralwidget)
        self.label_software.setObjectName("label_software")
        self.label_software.setText("软件版本号：" + SOFTWARE)
        self.label_software.setGeometry(QtCore.QRect(scaleSizeW(50), scaleSizeH(105), scaleSizeW(400), scaleSizeH(40)))
        self.label_software.setStyleSheet(
            "QLabel#label_software{"
            "font-size: 22px;"
            "color: rgb(255,255,255)}"
        )

        # 设置系统时间
        self.label_set_time = QtWidgets.QLabel(self.centralwidget)
        self.label_set_time.setObjectName("label_set_time")
        self.label_set_time.setText("设置系统时间")
        self.label_set_time.setGeometry(QtCore.QRect(scaleSizeW(50), scaleSizeH(150), scaleSizeW(200), scaleSizeH(40)))
        self.label_set_time.setStyleSheet(
            "QLabel#label_set_time{"
            "font-size: 22px;"
            "background-color: transparent;"
            "color: rgb(255,255,255)}"
        )
        # 设置系统时间的按钮，覆盖在标签上实现点击
        self.btn_set_time = QtWidgets.QPushButton(self.centralwidget)
        self.btn_set_time.setObjectName("label_set_time")
        self.btn_set_time.setFlat(True)
        self.btn_set_time.setGeometry(QtCore.QRect(scaleSizeW(50), scaleSizeH(150), scaleSizeW(150), scaleSizeH(40)))
        self.btn_set_time.clicked.connect(self.__set_time_click)
        self.btn_set_time.setStyleSheet(
            "QPushButton#btn_set_time{"
            "font-size: 22px;"
            "background-color: transparent;"
            "color: rgb(0,0,0)}"
        )

        # 设置
        MainWindow.setCentralWidget(self.centralwidget)
        # 窗口背景透明
        MainWindow.setAttribute(QtCore.Qt.WA_TranslucentBackground)

    def __shut(self):
        """
        关机
        """
        # 弹框提示
        self.shutDialog = MsgBoxDialog(
            string_dict("shutTip"),
            string_dict("shutMsg"),
            operate_dict("shut"), shut,
            operate_dict("cancel"), None
        )
        self.shutDialog.show()

    def __set_time_click(self):
        """
        点击修改时间
        """
        self.setDateTime = SetDateTime()
        self.setDateTime.show()


if __name__ == '__main__':
    app = QApplication(sys.argv)
    desktop = QApplication.desktop()
    setDesktop(desktop)

    app.setAttribute(QtCore.Qt.AA_EnableHighDpiScaling)
    myWin = SettingsDialog()

    myWin.showFullScreen()
    sys.exit(app.exec_())
