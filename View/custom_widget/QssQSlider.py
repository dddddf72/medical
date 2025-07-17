#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Created on 2018年5月15日
@author: Irony
@site: https://pyqt.site , https://github.com/PyQt5
@email: 892768447@qq.com
@file: QssQSlider
@description: 通过QSS美化QSlider
"""

try:
    from PyQt5.QtCore import Qt
    from PyQt5.QtWidgets import QApplication, QWidget, QVBoxLayout, QSlider
except ImportError:
    from PySide2.QtCore import Qt
    from PySide2.QtWidgets import QApplication, QWidget, QVBoxLayout, QSlider

StyleSheet = """

QSlider::groove:horizontal {
    border: 1px solid #4A708B;
    background: #C0C0C0;
    height: 5px;
    border-radius: 1px;
    padding-left:-1px;
    padding-right:-1px;
}

QSlider::sub-page:horizontal {
    background: qlineargradient(x1:0, y1:0, x2:0, y2:1, 
        stop:0 #128194, stop:1 #128194);
    background: qlineargradient(x1: 0, y1: 0.2, x2: 1, y2: 1,
        stop: 0 #128194, stop: 1 #128194);
    border: 1px solid #128194;
    height: 10px;
    border-radius: 2px;
}

QSlider::add-page:horizontal {
    background: #222129;
    border: 0px solid #777;
    height: 10px;
    border-radius: 2px;
}

QSlider::handle:horizontal 
{
    background: qradialgradient(spread:pad, cx:0.5, cy:0.5, radius:0.5, fx:0.5, fy:0.5, 
    stop:0.6 #128194, stop:0.778409 rgba(255, 255, 255, 255));

    width: 15px;
    margin: -7px -7px -7px -7px; 
    border-radius: 5px;
}

QSlider::handle:horizontal:hover {
    background: qradialgradient(spread:pad, cx:0.5, cy:0.5, radius:0.5, fx:0.5, fy:0.5, stop:0.6 #2A8BDA, 
    stop:0.778409 rgba(255, 255, 255, 255));

    width: 15px;
    margin: -7px -7px -7px -7px; 
    border-radius: 5px;
}

QSlider::sub-page:horizontal:disabled {
    background: #00009C;
    border-color: #999;
}

QSlider::add-page:horizontal:disabled {
    background: #eee;
    border-color: #999;
}

QSlider::handle:horizontal:disabled {
    background: #eee;
    border: 1px solid #aaa;
    border-radius: 4px;
}

/*竖向*/
QSlider::groove:vertical {
    border: 1px solid #4A708B;
    background: #C0C0C0;
    width: 5px;
    border-radius: 1px;
    padding-left:-1px;
    padding-right:-1px;
    padding-top:-1px;
    padding-bottom:-1px;
}

QSlider::sub-page:vertical {
    background: #575757;
    border: 1px solid #4A708B;
    border-radius: 2px;
}

QSlider::add-page:vertical {
    background: qlineargradient(x1:0, y1:0, x2:0, y2:1, 
        stop:0 #c4c4c4, stop:1 #B1B1B1);
    background: qlineargradient(x1: 0, y1: 0.2, x2: 1, y2: 1,
        stop: 0 #5DCCFF, stop: 1 #1874CD);
    border: 0px solid #777;
    width: 10px;
    border-radius: 2px;
}

QSlider::handle:vertical 
{
	background: qradialgradient(spread:pad, cx:0.5, cy:0.5, radius:0.5, fx:0.5, fy:0.5, stop:0.6 #45ADED, 
    stop:0.778409 rgba(255, 255, 255, 255));
    height: 11px;
    margin-left: -3px;
    margin-right: -3px;
    border-radius: 5px;
}

QSlider::sub-page:vertical:disabled {
    background: #00009C;
    border-color: #999;
}

QSlider::add-page:vertical:disabled {
    background: #eee;
    border-color: #999;
}

QSlider::handle:vertical:disabled {
    background: #eee;
    border: 1px solid #aaa;
    border-radius: 4px;
}
"""


class QssQSlider(QSlider):

    def __init__(self, *args, **kwargs):
        super(QssQSlider, self).__init__(*args, **kwargs)

class Window(QWidget):

    def __init__(self, *args, **kwargs):
        super(Window, self).__init__(*args, **kwargs)
        self.setAttribute(Qt.WA_StyledBackground, True)
        layout = QVBoxLayout(self)
        layout.addWidget(QssQSlider(Qt.Vertical, self))
        layout.addWidget(QssQSlider(Qt.Horizontal, self))


if __name__ == '__main__':
    import sys

    app = QApplication(sys.argv)
    app.setStyleSheet(StyleSheet)
    w = Window()
    w.show()
    sys.exit(app.exec_())
