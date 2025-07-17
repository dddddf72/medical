import sys

import PyQt5.QtCore as QtCore
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QPixmap, QPainter
from PyQt5.QtWidgets import QWidget, QApplication, QPushButton

from Utils.Path import rootPath
from Utils.ResolutionTools import scaleSizeW, scaleSizeH

imgPath = rootPath + "/View/img"

class PixWindow(QWidget):  # 不规则窗体
    def __init__(self):
        super().__init__()
        self.pix = QPixmap(imgPath + "/selfcheck/弹出框_05.png")
        windowWidth = scaleSizeW(560)
        windowHeight = scaleSizeH(330)
        self.resize(windowWidth, windowHeight)
        self.pix = self.pix.scaled(int(windowWidth), int(windowHeight))
        self.setMask(self.pix.mask())
        self.setWindowFlags(Qt.FramelessWindowHint | QtCore.Qt.WindowStaysOnTopHint)  # 设置无边框和置顶窗口样式

        self.pushButton = QPushButton(self)
        self.pushButton.setObjectName(u"pushButton")
        self.pushButton.setGeometry(QtCore.QRect(scaleSizeW(130), scaleSizeH(220), scaleSizeW(120), scaleSizeH(40)))
        self.pushButton.setStyleSheet(u"border-image: url(" + imgPath + "/selfcheck/弹出框_06.png);")

        self.pushButton_2 = QPushButton(self)
        self.pushButton_2.setObjectName(u"pushButton_2")
        self.pushButton_2.setGeometry(QtCore.QRect(scaleSizeW(330), scaleSizeH(220), scaleSizeW(120), scaleSizeH(40)))
        self.pushButton_2.setStyleSheet(u"border-image: url(" + imgPath + "/selfcheck/弹出框_08.png);")


    def paintEvent(self, event):  # 绘制窗口
        paint = QPainter(self)
        paint.drawPixmap(0, 0, self.pix.width(), self.pix.height(), self.pix)


if __name__ == '__main__':
    app = QApplication(sys.argv)
    win = PixWindow()
    win.show()
    sys.exit(app.exec_())