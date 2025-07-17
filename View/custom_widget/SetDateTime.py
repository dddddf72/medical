import os
import sys
import threading

from PyQt5 import QtCore, QtWidgets
from PyQt5.QtCore import Qt, QDateTime
from PyQt5.QtWidgets import QMainWindow, QWidget, QApplication

from Utils.DeviceUtil import osk
from Utils.Log import log
from Utils.ResolutionTools import scaleSizeW, scaleSizeH, setDesktop


class SetDateTime(QMainWindow):
    """
    设置时间
    """
    def __init__(self):
        super(SetDateTime, self).__init__()
        # 界面
        self.setupUi(self)
        # 显示软键盘
        oskThread = threading.Thread(target=osk)
        oskThread.start()

    def setupUi(self, MainWindow):
        MainWindow.setObjectName("MainWindow")
        MainWindow.resize(scaleSizeW(250), scaleSizeH(100))
        MainWindow.setWindowTitle("系统时间设置")
        # 禁止修改大小，永远置顶
        MainWindow.setWindowFlags(
            Qt.WindowCloseButtonHint
            | Qt.MSWindowsFixedSizeDialogHint
            | Qt.WindowStaysOnTopHint
        )

        # 布局
        self.centralwidget = QWidget(MainWindow)
        self.centralwidget.setObjectName(u"centralwidget")
        self.centralwidget.setStyleSheet(
            "QWidget#centralwidget{"
            "background-color: rgb(231, 234, 237)}"
        )

        # label
        # self.timeLabel = QtWidgets.QLabel(self.centralwidget)
        # self.timeLabel.setAlignment(QtCore.Qt.AlignRight | QtCore.Qt.AlignVCenter)
        # self.timeLabel.setGeometry(QtCore.QRect(scaleSizeW(0), scaleSizeH(20), scaleSizeW(80), scaleSizeH(25)))
        # self.timeLabel.setObjectName("timeLabel")
        # self.timeLabel.setText("系统时间设置")
        # self.timeLabel.setStyleSheet(
        #     "QLabel#timeLabel{"
        #     "font-size: 16px;"
        #     "color: rgb(0,0,0);"
        #     "padding: 0px 0px}"
        # )

        # 时间修改控件
        self.dateTimeEdit = QtWidgets.QDateTimeEdit(QDateTime.currentDateTime(), self.centralwidget)
        self.dateTimeEdit.setDisplayFormat("yyyy-MM-dd HH:mm:ss")
        self.dateTimeEdit.setStyleSheet(
            "QDateTimeEdit#date_time_edit{"
            "font-size: 18px;"
            "color: rgb(0,0,0)}"
        )
        self.dateTimeEdit.setGeometry(QtCore.QRect(scaleSizeW(15), scaleSizeH(20), scaleSizeW(220), scaleSizeH(25)))
        self.dateTimeEdit.setObjectName("date_time_edit")

        # 取消按钮
        self.noPushButton = QtWidgets.QPushButton(self.centralwidget)
        self.noPushButton.setObjectName("no_push_button")
        self.noPushButton.setText("取消")
        self.noPushButton.setGeometry(QtCore.QRect(scaleSizeW(40), scaleSizeH(70), scaleSizeW(60), scaleSizeH(20)))
        self.noPushButton.clicked.connect(self.__no_btn_click)

        # 确认按钮
        self.yesPushButton = QtWidgets.QPushButton(self.centralwidget)
        self.yesPushButton.setObjectName("yes_push_button")
        self.yesPushButton.setText("确认")
        self.yesPushButton.setGeometry(QtCore.QRect(scaleSizeW(150), scaleSizeH(70), scaleSizeW(60), scaleSizeH(20)))
        self.yesPushButton.clicked.connect(self.__yes_btn_click)

        # 设置
        MainWindow.setCentralWidget(self.centralwidget)
        # 窗口背景透明
        MainWindow.setAttribute(QtCore.Qt.WA_TranslucentBackground)

    def __no_btn_click(self):
        """
        取消按钮点击
        """
        self.close()

    def __yes_btn_click(self):
        """
        确认按钮点击
        """
        # 修改系统时间
        dataTime = self.dateTimeEdit.dateTime()
        data = "date %d-%d-%d" % (dataTime.date().year(), dataTime.date().month(), dataTime.date().day())
        time = "time %d:%d:%d" % (dataTime.time().hour(), dataTime.time().minute(), dataTime.time().second())
        log("修改系统时间", data + "  " + time)
        os.system(data)
        os.system(time)
        # 修改时间显示
        self.dateTimeEdit.setDateTime(QDateTime.currentDateTime())
        self.close()


if __name__ == '__main__':
    app = QApplication(sys.argv)
    desktop = QApplication.desktop()
    setDesktop(desktop)

    app.setAttribute(QtCore.Qt.AA_EnableHighDpiScaling)
    myWin = SetDateTime()
    myWin.show()
    sys.exit(app.exec_())
