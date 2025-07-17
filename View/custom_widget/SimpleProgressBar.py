#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Created on 2018年1月30日
@author: Irony
@site: https://pyqt.site , https://github.com/PyQt5
@email: 892768447@qq.com
@file: SimpleStyle
@description:
"""

import sys

from PyQt5.QtWidgets import QWidget, QApplication, QVBoxLayout, QProgressBar

from Utils.Path import rootPath

# 图片所在路径
imgPath = rootPath + "/View/img"

StyleSheet = """
#PreheatProgressBar {
    border: 4px solid;
    border-image: url(""" + imgPath + """/preheat/进度条_03.png)
}
#PreheatProgressBar::chunk {
    border-radius: 6px;
    background-image: url(""" + imgPath + """/preheat/预热进度_11.png)
}

#SelfcheckProgressBar {
    border: 3px solid;
    border-image: url(""" + imgPath + """/selfcheck/进度条_15.png)
}
#SelfcheckProgressBar::chunk {
    border-radius: 6px;
    border-image: url(""" + imgPath + """/selfcheck/进度条_11.png)
}

"""

class SimpleProgressBar(QProgressBar):

    def __init__(self, *args, **kwargs):
        super(SimpleProgressBar, self).__init__(*args, **kwargs)
        self.setValue(0)

class Window(QWidget):

    def __init__(self, *args, **kwargs):
        super(Window, self).__init__(*args, **kwargs)
        self.resize(800, 600)
        layout = QVBoxLayout(self)
        layout.addWidget(
            SimpleProgressBar(self, minimum=0, maximum=100, objectName="RedProgressBar"))
        layout.addWidget(  # 繁忙状态
            SimpleProgressBar(self, minimum=0, maximum=0, objectName="RedProgressBar"))

        layout.addWidget(
            SimpleProgressBar(self, minimum=0, maximum=100, textVisible=False,
                        objectName="GreenProgressBar"))
        layout.addWidget(
            SimpleProgressBar(self, minimum=0, maximum=0, textVisible=False,
                        objectName="GreenProgressBar"))

        layout.addWidget(
            SimpleProgressBar(self, minimum=0, maximum=100, textVisible=False,
                        objectName="BlueProgressBar"))
        layout.addWidget(
            SimpleProgressBar(self, minimum=0, maximum=0, textVisible=False,
                        objectName="BlueProgressBar"))


if __name__ == "__main__":
    app = QApplication(sys.argv)
    app.setStyleSheet(StyleSheet)
    w = Window()
    w.show()
    sys.exit(app.exec_())

