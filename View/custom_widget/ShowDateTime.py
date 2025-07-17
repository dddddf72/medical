import sys

from PyQt5 import QtCore, QtWidgets
from PyQt5.QtCore import Qt, QDateTime, QTimer
from PyQt5.QtWidgets import QMainWindow, QWidget, QApplication

from Utils.ResolutionTools import scaleSizeW, scaleSizeH, setDesktop


class ShowDateTime(QMainWindow):
    """
    显示时间
    """
    def __init__(self):
        super(ShowDateTime, self).__init__()
        # 界面
        self.setupUi(self)
        # 定时更新时间
        self.updateTimer = QTimer()
        self.updateTimer.timeout.connect(self.update_current_time)
        self.updateTimer.start(1000)

    def setupUi(self, MainWindow):
        MainWindow.setObjectName("MainWindow")
        MainWindow.resize(scaleSizeW(400), scaleSizeH(30))
        # 无边框 永远置顶
        MainWindow.setWindowFlags(Qt.FramelessWindowHint | Qt.WindowStaysOnTopHint)
        # 布局
        self.centralwidget = QWidget(MainWindow)
        self.centralwidget.setObjectName(u"centralwidget")

        # 时间控件
        self.dateTimeLabel = QtWidgets.QLabel(self.centralwidget)
        self.dateTimeLabel.setStyleSheet(
            "QLabel#date_time_label{"
            "font-size: 18px;"
            "color: rgb(255,255,255);"
            "padding: 0px 10px}"
        )
        self.dateTimeLabel.setAlignment(QtCore.Qt.AlignRight | QtCore.Qt.AlignVCenter)
        self.dateTimeLabel.setGeometry(QtCore.QRect(scaleSizeW(0), scaleSizeH(0), scaleSizeW(400), scaleSizeH(30)))
        self.dateTimeLabel.setObjectName("date_time_label")

        # 设置
        MainWindow.setCentralWidget(self.centralwidget)
        # 窗口背景透明
        MainWindow.setAttribute(QtCore.Qt.WA_TranslucentBackground)
        MainWindow.move(scaleSizeW(880), scaleSizeH(690))

    def update_current_time(self):
        """
        更新当前时间
        """
        self.dateTimeLabel.setText(QDateTime.currentDateTime().toString("系统时间：yyyy-MM-dd HH:mm:ss"))


if __name__ == '__main__':
    app = QApplication(sys.argv)
    desktop = QApplication.desktop()
    setDesktop(desktop)

    app.setAttribute(QtCore.Qt.AA_EnableHighDpiScaling)
    myWin = ShowDateTime()
    myWin.show()
    sys.exit(app.exec_())
