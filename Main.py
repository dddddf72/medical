#! /usr/bin/env python
# -*- coding: utf-8 -*-
import os
import shutil
import sys
import threading
import traceback

from PyQt5 import QtCore
from PyQt5.QtWidgets import QApplication

from Config.Config import config
from Presenter.MainPresenter import MainPresenter
from Utils.DeviceUtil import stop
from Utils.Log import log
from Utils.Path import storagePath, rootPath
from Utils.ResolutionTools import setDesktop
from Utils.SoundUtil import SoundUtil
from View.custom_widget.ShowDateTime import ShowDateTime
from View.custom_widget.SimpleProgressBar import StyleSheet


def clean_temp():
    """
    清理临时文件夹

    当软件异常关闭时：未关闭软件就关机；关闭控制台强行杀死进程等
    会导致C盘中的临时文件夹得不到清理
    该情况只有在 pyinstaller -F 打包方式时出现，只有这种打包方式才会在C盘解压出临时文件夹
    """
    # 读取上次保存的临时文件夹
    lastTemp = config.last_temp

    # 临时文件夹存在 and 不是存储文件夹 and 不是本次运行文件夹，清理该临时文件夹
    if lastTemp is not None \
            and os.path.exists(lastTemp)\
            and lastTemp != storagePath \
            and lastTemp != rootPath:
        log("delete last_temp", lastTemp)
        try:
            shutil.rmtree(lastTemp)
        except BaseException as err:
            log("error delete last_temp", str(err))
    else:
        log("unnecessary delete last_temp", lastTemp)

    # 保存本次运行的临时文件夹
    config.set_last_temp(rootPath)


if __name__ == '__main__':
    try:
        app = QApplication(sys.argv)

        # 屏幕配置
        desktop = QApplication.desktop()
        setDesktop(desktop)
        # 高清屏幕自适应设置
        app.setAttribute(QtCore.Qt.AA_EnableHighDpiScaling)
        # 样式
        app.setStyleSheet(StyleSheet)

        # 预热界面，开始初始化
        mainPresenter = MainPresenter()
        mainPresenter.show()
        mainPresenter.power_up_init()

        # 时钟界面
        dateTime = ShowDateTime()
        dateTime.show()

        # 设置音量最大
        # 使用子线程调节音量，否则可能会卡死主线程的运行
        volumeThread = threading.Thread(target=SoundUtil.system_volume_max)
        volumeThread.start()

        # 清理
        clean_temp()

        sys.exit(app.exec_())
    except BaseException as error:
        log("应用退出")
        # 关闭应用前
        stop()
        # 并不能捕获子线程的异常信息
        log(repr(error))
        log(traceback.format_exc(limit=100))
