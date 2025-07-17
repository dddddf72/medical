import sys

from PyQt5 import QtCore, QtWidgets
from PyQt5.QtCore import Qt, QRect
from PyQt5.QtGui import QPixmap
from PyQt5.QtWidgets import QMainWindow, QWidget, QPushButton, QApplication

from Utils.Path import rootPath
from Utils.ResolutionTools import scaleSizeW, scaleSizeH, setDesktop

# 图片所在路径
imgPath = rootPath + "/View/img"


class MsgBoxDialog(QMainWindow):
    """
    提示
    """
    def __init__(self, title, content, left_btn, left_slot, right_btn, right_slot, stays_top=True):
        super(MsgBoxDialog, self).__init__()
        # 数据保存
        self.title = title
        self.content = content
        self.left_btn = left_btn
        self.left_slot = left_slot
        self.right_btn = right_btn
        self.right_slot = right_slot
        self.stays_top = stays_top
        # 界面
        self.setupUi(self)

    def right_btn_click(self):
        if self.right_slot is not None:
            self.right_slot()
        self.close()

    def left_btn_click(self):
        if self.left_slot is not None:
            self.left_slot()
        self.close()

    def setupUi(self, MainWindow):
        MainWindow.setObjectName("MainWindow")
        MainWindow.resize(scaleSizeW(566), scaleSizeH(332))
        if self.stays_top:
            # 无边框 永远置顶
            MainWindow.setWindowFlags(Qt.FramelessWindowHint | Qt.WindowStaysOnTopHint)
        else:
            # 无边框
            MainWindow.setWindowFlags(Qt.FramelessWindowHint)

        # 布局
        self.centralwidget = QWidget(MainWindow)
        self.centralwidget.setObjectName(u"centralwidget")

        # 背景图
        self.label_bg = QtWidgets.QLabel(self.centralwidget)
        self.label_bg.setScaledContents(True)
        self.label_bg.setPixmap(QPixmap(imgPath + "/selfcheck/弹出框_05.png"))
        self.label_bg.setGeometry(QtCore.QRect(scaleSizeW(0), scaleSizeH(0), scaleSizeW(566), scaleSizeH(332)))
        self.label_bg.setObjectName("label_bg")

        # 标题
        self.label_title = QtWidgets.QLabel(self.centralwidget)
        self.label_title.setScaledContents(True)
        self.label_title.setObjectName("label_title")
        self.label_title.setText(self.title)
        self.label_title.setGeometry(QtCore.QRect(scaleSizeW(0), scaleSizeH(60), scaleSizeW(566), scaleSizeH(25)))
        self.label_title.setStyleSheet(
            "QLabel#label_title{"
            "font-size: 23px;"
            "font-weight: bold;"
            "color: rgb(255,255,255);"
            "padding: 0px 60px}"
        )
        # 居中
        self.label_title.setAlignment(Qt.AlignCenter)

        # 内容
        self.label_content = QtWidgets.QLabel(self.centralwidget)
        self.label_content.setScaledContents(True)
        self.label_content.setObjectName("label_content")
        self.label_content.setText(self.content)
        self.label_content.setGeometry(QtCore.QRect(scaleSizeW(0), scaleSizeH(70), scaleSizeW(566), scaleSizeH(130)))
        self.label_content.setStyleSheet(
            "QLabel#label_content{"
            "font-size: 20px;"
            "color: rgb(255,255,255);"
            "padding: 0px 60px}"
        )
        # 居中
        self.label_content.setAlignment(Qt.AlignCenter)
        # 长文本自动换行
        self.label_content.setWordWrap(True)

        # 左边按钮
        if self.left_btn is not None:
            self.leftPushButton = QPushButton(self.centralwidget)
            self.leftPushButton.setObjectName(u"leftPushButton")
            self.leftPushButton.setGeometry(QRect(scaleSizeW(130), scaleSizeH(220), scaleSizeW(120), scaleSizeH(40)))
            self.leftPushButton.setText(self.left_btn)
            self.leftPushButton.setStyleSheet(
                "QPushButton#leftPushButton{"
                "font-size: 20px;"
                "color: rgb(47,60,139);"
                "border-radius: 10px;"
                "font-weight: bold;"
                "background-color: rgb(240,240,240)}"
            )
            self.leftPushButton.clicked.connect(self.left_btn_click)

        # 右边按钮
        if self.right_btn is not None:
            self.rightPushButton = QPushButton(self.centralwidget)
            self.rightPushButton.setObjectName(u"rightPushButton")
            self.rightPushButton.setGeometry(QRect(scaleSizeW(330), scaleSizeH(220), scaleSizeW(120), scaleSizeH(40)))
            self.rightPushButton.setText(self.right_btn)
            self.rightPushButton.setStyleSheet(
                "QPushButton#rightPushButton{"
                "font-size: 20px;"
                "color: rgb(47,60,139);"
                "border-radius: 10px;"
                "font-weight: bold;"
                "background-color: rgb(188,214,247)}"
            )
            self.rightPushButton.clicked.connect(self.right_btn_click)

        # 设置
        MainWindow.setCentralWidget(self.centralwidget)
        # 窗口背景透明
        MainWindow.setAttribute(QtCore.Qt.WA_TranslucentBackground)


if __name__ == '__main__':
    app = QApplication(sys.argv)
    desktop = QApplication.desktop()
    setDesktop(desktop)

    app.setAttribute(QtCore.Qt.AA_EnableHighDpiScaling)
    myWin = MsgBoxDialog("提示", "请先装配无菌护套再进行下一步操作", "你好", None, "你好", None)

    myWin.showFullScreen()
    sys.exit(app.exec_())
