import os
import sys

from Config.Config import config
from Drive.DriveManager import driveManager
from Utils.Log import log


def shut():
    """
    关机
    """
    log("shut")
    # 关闭应用前
    stop()
    # 关机
    os.system("shutdown -s -t 1")
    # 关机前需要退出软件，避免异常杀死进程，C盘临时文件得不到清理
    sys.exit()


def reboot():
    """
    重启
    """
    log("reboot")
    # 关闭应用前
    stop()
    # 重启
    os.system("shutdown -r -t 1")
    # 重启前需要退出软件，避免异常杀死进程，C盘临时文件得不到清理
    sys.exit()


def restart_app():
    """
    重启应用
    """
    log("重启应用")
    # 关闭应用前
    stop()
    # 仅在打包后的exe时才生效
    python = sys.executable
    os.execl(python, python, *sys.argv)


def stop():
    """
    关闭应用前的操作
    """
    log("stop")
    # 关闭激光器 和 光开关
    if not config.model_is_debug:
        driveManager.laser_drive.set_enable(False)
        driveManager.handle_drive.light_switch(False)


def exit_app():
    """
    关闭应用
    """
    log("exit_app")
    # 关闭应用前
    stop()
    # 退出
    sys.exit()


def explorer():
    """
    打开桌面
    """
    log("explorer")
    os.system("explorer.exe")


def osk():
    """
    打开软键盘
    """
    log("osk")
    os.system("osk")


