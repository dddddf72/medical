import threading
import time
import tkinter
from tkinter import filedialog

from PyQt5.QtCore import QTimer
from PyQt5.QtWidgets import QMainWindow, QMessageBox

from Config.Config import *
from Drive.DriveManager import driveManager
from Drive.laser.LaserDrive import get_laser_power
from Utils.DeviceUtil import restart_app, explorer, exit_app, osk
from Utils.Log import log
from Utils.SurgicalData import PATH_SURGICAL_DATA
from View.config.config import Ui_MainWindow

# 应用名
APP_NAME = "parathyroid"
EXE_NAME = APP_NAME + ".exe"


def model_is_release(func):
    """
    仅在 model 层为 release 时才执行的装饰器
    :param func: 被装饰的函数
    :return: handle
    """
    def handle(*args, **kwargs):
        """
        处理函数
        :param args: 被装饰函数的参数
        :param kwargs: 被装饰函数的参数
        :return: 被装饰函数的返回值，未执行返回False
        """
        # model 层是 debug 时不做处理
        if config.model_is_debug:
            return False
        # 正常执行
        return func(args[0])

    return handle


class ConfigView(QMainWindow, Ui_MainWindow):
    def __init__(self):
        super(ConfigView, self).__init__()
        self.setupUi(self)
        self.__init_ui()

    def __init_ui(self):
        """
        初始化界面
        """
        # 启动定时器，周期检查易变信息，间隔时间：100ms
        self.__realTimer = QTimer(self)
        self.__realTimer.timeout.connect(self.__real_timeout)
        self.__realTimer.start(100)

        # 信号
        # 重启
        self.rebootPushButton.clicked.connect(self.reboot)
        # 恢复出厂设置
        self.recoveryPushButton.clicked.connect(self.recovery)
        # 导出
        self.exportPushButton.clicked.connect(self.export)
        # 软件更新
        self.updatePushButton.clicked.connect(self.update)
        # 固化配置
        self.solidifyConfigPushButton.clicked.connect(self.solidify_config)
        # 激光器控制
        self.openLaserPushButton.clicked.connect(self.open_laser)
        self.closeLaserPushButton.clicked.connect(self.close_laser)
        # 光开关控制
        self.openLightPushButton.clicked.connect(self.open_light)
        self.closeLightPushButton.clicked.connect(self.close_light)
        # 检测键模拟
        self.readShortPushButton.clicked.connect(self.read_short)
        self.readPressPushButton.clicked.connect(self.read_press)
        self.readBouncePushButton.clicked.connect(self.read_bounce)
        # 模式键模拟
        self.modeShortPushButton.clicked.connect(self.mode_short)
        self.modePressPushButton.clicked.connect(self.mode_press)
        self.modeBouncePushButton.clicked.connect(self.mode_bounce)
        # 快捷方式
        self.exitPushButton.clicked.connect(exit_app)
        self.explorerPushButton.clicked.connect(explorer)
        self.oskPushButton.clicked.connect(self.open_osk)

        # 基础配置
        # 序列号
        self.snLineEdit.setText(str(config.serial_number))
        self.snLineEdit.textChanged.connect(config.set_serial_number)
        # view
        self.viewComboBox.addItems([EDITION_DEBUG, EDITION_RELEASE])
        self.viewComboBox.setCurrentText(config.view)
        self.viewComboBox.activated[str].connect(config.set_view)
        # model
        self.modelComboBox.addItems([EDITION_DEBUG, EDITION_RELEASE])
        self.modelComboBox.setCurrentText(config.model)
        self.modelComboBox.activated[str].connect(config.set_model)
        # log
        self.logComboBox.addItems([EDITION_DEBUG, EDITION_RELEASE])
        self.logComboBox.setCurrentText(config.log)
        self.logComboBox.activated[str].connect(config.set_log)
        # log print
        self.logPrintComboBox.addItems([str(True), str(False)])
        self.logPrintComboBox.setCurrentText(str(config.log_print))
        self.logPrintComboBox.activated[str].connect(config.set_log_print)
        # 音量
        self.volumeDoubleSpinBox.setMinimum(0)
        self.volumeDoubleSpinBox.setMaximum(1)
        self.volumeDoubleSpinBox.setValue(config.volume)
        self.volumeDoubleSpinBox.valueChanged.connect(config.set_volume)
        # 数据采集卡设备id
        self.niDeviceIdLineEdit.setText(str(config.ni_device_id))
        self.niDeviceIdLineEdit.textChanged.connect(config.set_ni_device_id)
        # 采集数据的系数
        self.niRatioDoubleSpinBox.setValue(config.ni_ratio)
        self.niRatioDoubleSpinBox.valueChanged.connect(config.set_ni_ratio)
        # 采集数据的补偿
        self.niCompensateDoubleSpinBox.setMinimum(-100)
        self.niCompensateDoubleSpinBox.setValue(config.ni_compensate)
        self.niCompensateDoubleSpinBox.valueChanged.connect(config.set_ni_compensate)
        # 长按读值
        self.readLongComboBox.addItems([str(True), str(False)])
        self.readLongComboBox.setCurrentText(str(config.read_long))
        self.readLongComboBox.activated[str].connect(config.set_read_long)

        # 预热界面
        # 预热时长，单位：分钟
        self.preheatSpinBox.setMinimum(0)
        self.preheatSpinBox.setMaximum(30)
        self.preheatSpinBox.setValue(config.preheat_time)
        self.preheatSpinBox.valueChanged.connect(config.set_preheat_time)
        # 激光功率
        self.laserPowerSpinBox.setMinimum(10)
        self.laserPowerSpinBox.setMaximum(500)
        self.laserPowerSpinBox.setValue(config.laser_power)
        self.laserPowerSpinBox.valueChanged.connect(self.set_laser_power)
        # 激光功率损耗补偿
        self.laserPowerCompensateSpinBox.setMinimum(-50)
        self.laserPowerCompensateSpinBox.setMaximum(50)
        self.laserPowerCompensateSpinBox.setValue(config.laser_power_compensate)
        self.laserPowerCompensateSpinBox.valueChanged.connect(config.set_laser_power_compensate)
        # 激光功率最小值
        self.laserPowerMinSpinBox.setMinimum(0)
        self.laserPowerMinSpinBox.setMaximum(600)
        self.laserPowerMinSpinBox.setValue(config.laser_power_min)
        self.laserPowerMinSpinBox.valueChanged.connect(config.set_laser_power_min)
        # 激光功率最大值
        self.laserPowerMaxSpinBox.setMinimum(0)
        self.laserPowerMaxSpinBox.setMaximum(600)
        self.laserPowerMaxSpinBox.setValue(config.laser_power_max)
        self.laserPowerMaxSpinBox.valueChanged.connect(config.set_laser_power_max)
        # 检查间隔时间
        self.laserCheckIntervalDoubleSpinBox.setValue(config.laser_check_interval)
        self.laserCheckIntervalDoubleSpinBox.valueChanged.connect(config.set_laser_check_interval)
        # 稳定检查次数
        self.laserStableCheckMaxSpinBox.setMinimum(1)
        self.laserStableCheckMaxSpinBox.setValue(config.laser_stable_check_max)
        self.laserStableCheckMaxSpinBox.valueChanged.connect(config.set_laser_stable_check_max)
        # 最高重试次数
        self.laserCheckRetryMaxSpinBox.setMinimum(1)
        self.laserCheckRetryMaxSpinBox.setMaximum(1000)
        self.laserCheckRetryMaxSpinBox.setValue(config.laser_check_retry_max)
        self.laserCheckRetryMaxSpinBox.valueChanged.connect(config.set_laser_check_retry_max)

        # 偏置电压
        # 偏置电压取值次数
        self.offsetTimesSpinBox.setMinimum(0)
        self.offsetTimesSpinBox.setMaximum(100)
        self.offsetTimesSpinBox.setValue(config.offset_times)
        self.offsetTimesSpinBox.valueChanged.connect(config.set_offset_times)
        # 偏置电压最小值
        self.offsetMinDoubleSpinBox.setDecimals(3)
        self.offsetMinDoubleSpinBox.setMinimum(-1)
        self.offsetMinDoubleSpinBox.setMaximum(1)
        self.offsetMinDoubleSpinBox.setValue(config.offset_min)
        self.offsetMinDoubleSpinBox.valueChanged.connect(config.set_offset_min)
        # 偏置电压最大值
        self.offsetMaxDoubleSpinBox.setDecimals(3)
        self.offsetMaxDoubleSpinBox.setMinimum(-1)
        self.offsetMaxDoubleSpinBox.setMaximum(1)
        self.offsetMaxDoubleSpinBox.setValue(config.offset_max)
        self.offsetMaxDoubleSpinBox.valueChanged.connect(config.set_offset_max)

        # 自检界面
        # 仿体预设荧光值
        self.presetImitationFluorescenceDoubleSpinBox.setValue(config.preset_imitation_fluorescence)
        self.presetImitationFluorescenceDoubleSpinBox.valueChanged.connect(config.set_preset_imitation_fluorescence)
        # 荧光值的最大差值
        self.fluorescenceDifferenceMaxDoubleSpinBox.setMaximum(1000)
        self.fluorescenceDifferenceMaxDoubleSpinBox.setValue(config.fluorescence_difference_max)
        self.fluorescenceDifferenceMaxDoubleSpinBox.valueChanged.connect(config.set_fluorescence_difference_max)

        # 取基准值界面
        # 基准值的最小值
        self.referentMinDoubleSpinBox.setDecimals(3)
        self.referentMinDoubleSpinBox.setMinimum(0)
        self.referentMinDoubleSpinBox.setValue(config.referent_min)
        self.referentMinDoubleSpinBox.valueChanged.connect(config.set_referent_min)
        # 基准值的最大值
        self.referentMaxDoubleSpinBox.setDecimals(3)
        self.referentMaxDoubleSpinBox.setMaximum(100)
        self.referentMaxDoubleSpinBox.setValue(config.referent_max)
        self.referentMaxDoubleSpinBox.valueChanged.connect(config.set_referent_max)
        # 取基准值的次数
        self.triesLimitSpinBox.setMinimum(5)
        self.triesLimitSpinBox.setMaximum(5)
        self.triesLimitSpinBox.setValue(config.tries_limit)
        self.triesLimitSpinBox.valueChanged.connect(config.set_tries_limit)

        # 采集界面
        # 短按报警时长,单位：秒
        self.playTimeSpinBox.setMinimum(1)
        self.playTimeSpinBox.setMaximum(100)
        self.playTimeSpinBox.setValue(config.play_time)
        self.playTimeSpinBox.valueChanged.connect(config.set_play_time)
        # 通过基准值得到阈值的倍数
        self.multipleThresholdDoubleSpinBox.setMinimum(1)
        self.multipleThresholdDoubleSpinBox.setValue(config.multiple_threshold)
        self.multipleThresholdDoubleSpinBox.valueChanged.connect(config.set_multiple_threshold)
        # 通过基准值得到阈值的倍数
        self.multipleRedDoubleSpinBox.setMinimum(1)
        self.multipleRedDoubleSpinBox.setValue(config.multiple_red)
        self.multipleRedDoubleSpinBox.valueChanged.connect(config.set_multiple_red)
        # 进度条能显示的基准值最大倍数
        self.multipleMaxDoubleSpinBox.setMinimum(1)
        self.multipleMaxDoubleSpinBox.setValue(config.multiple_max)
        self.multipleMaxDoubleSpinBox.valueChanged.connect(config.set_multiple_max)
        # 长按读值触发时长
        self.readLongTriggerDoubleSpinBox.setDecimals(1)
        self.readLongTriggerDoubleSpinBox.setMinimum(0.5)
        self.readLongTriggerDoubleSpinBox.setValue(config.read_long_trigger)
        self.readLongTriggerDoubleSpinBox.valueChanged.connect(config.set_read_long_trigger)

    def closeEvent(self, *args, **kwargs):
        # 停止实时检查的定时器
        self.__realTimer.stop()

    def reboot(self):
        """
        保存数据，重启应用
        """
        log("保存设置，重启应用")
        restart_app()

    def recovery(self):
        """
        恢复出厂设置
        """
        log("恢复出厂设置")
        os.remove(PATH_MODIFY)
        restart_app()

    def export(self):
        """
        导出手术记录文件
        """
        # 打开选择文件夹的对话框
        tkinter.Tk().withdraw()
        # 获取目标文件夹，生成目标文件
        target = filedialog.askdirectory() + "/手术数据.xlsx"
        log("export directory", target)
        # 复制到指定文件夹
        shutil.copyfile(PATH_SURGICAL_DATA, target)
        # 提示
        msg_box = QMessageBox(QMessageBox.Information, '操作成功', '文件路径: ' + target)
        msg_box.exec_()

    def update(self):
        """
        应用更新
        """
        # 打开选择文件夹的对话框
        tkinter.Tk().withdraw()
        # 检查合法性
        directory = filedialog.askdirectory()
        # 文件夹命名不合法
        if directory.split('/')[-1] != APP_NAME:
            msg_box = QMessageBox(QMessageBox.Warning, '错误', '该文件夹名字错误（正确文件夹名：%s），请选择正确路径，不得含有中文' % APP_NAME)
            msg_box.exec_()
            return

        # 文件不存在
        if not os.path.exists(directory + "/" + EXE_NAME):
            msg_box = QMessageBox(QMessageBox.Warning, '错误', '该目录下无新应用程序(%s)，请选择正确路径，不得含有中文' % EXE_NAME)
            msg_box.exec_()
            return

        # 文件存在，可以更新
        # 构建batch
        batPath = rootPath + "/update.bat"
        bat = open(batPath, "w")
        command = "@echo off" + "\n"
        # 关闭本应用
        command += "taskkill /f /im " + EXE_NAME + "\n"
        # 复制文件
        command += "xcopy " + directory.replace("/", "\\") + " " + storagePath.replace("/", "\\") + " /E /y\n"
        # 打开本应用
        command += "start " + storagePath.replace("/", "\\") + "\\" + EXE_NAME + "\n"
        command += "exit"
        # 写入
        bat.write(command)
        bat.close()
        log("batch", command)
        # 运行
        os.system("start " + batPath)

    @model_is_release
    def open_laser(self):
        """
        打开激光器
        """
        driveManager.laser_drive.set_enable(True)
        # 设置功率
        driveManager.laser_drive.set_power(get_laser_power())

    @model_is_release
    def close_laser(self):
        """
        关闭激光器
        """
        driveManager.laser_drive.set_enable(False)

    def open_light(self):
        """
        打开光开关
        """
        driveManager.handle_drive.light_switch(True)
        time.sleep(0.05)
        driveManager.handle_drive.light_switch_is_on()

    def close_light(self):
        """
        关闭光开关
        """
        driveManager.handle_drive.light_switch(False)
        time.sleep(0.05)
        driveManager.handle_drive.light_switch_is_on()

    def read_short(self):
        """
        检测键按下抬起，大于0.3s抬起
        """
        driveManager.read_simulate_btn_press()
        timer = QTimer(self)
        timer.singleShot(400, driveManager.read_simulate_btn_bounce)

    def read_press(self):
        """
        检测键长按，不抬起
        """
        driveManager.read_simulate_btn_press()

    def read_bounce(self):
        """
        检测键抬起
        """
        driveManager.read_simulate_btn_bounce()

    def mode_short(self):
        """
        模式键按下抬起，大于0.3s抬起
        """
        driveManager.mode_simulate_btn_press()
        timer = QTimer(self)
        timer.singleShot(400, driveManager.mode_simulate_btn_bounce)

    def mode_press(self):
        """
        模式键按下
        """
        driveManager.mode_simulate_btn_press()

    def mode_bounce(self):
        """
        模式键抬起
        """
        driveManager.mode_simulate_btn_bounce()

    def set_laser_power(self, value):
        """
        设置激光功率
        :param value: 功率
        """
        # 保存设置值
        config.set_laser_power(value)
        # 非 debug 状态，设置硬件激光功率
        if not config.model_is_debug:
            driveManager.laser_drive.set_power(get_laser_power())

    def __real_timeout(self):
        """
        实时信息超时回调
        用于便捷获取一些易变信息的当前值，仅做展示
        """
        # 数据采集卡数据
        self.niDataLabel.setText("%.4fV" % driveManager.fluorescence)
        # 采集卡信息
        self.niInfoLabel.setText(driveManager.get_ni_info())

        # 按键状态
        if not driveManager.button_enable:
            # 当前未使能，提示锁定状态
            self.readStatusLabel.setText("锁定")
            self.modeStatusLabel.setText("锁定")
        else:
            # 检测键
            if driveManager.read_btn_is_press(False):
                self.readStatusLabel.setText("按下")
            else:
                self.readStatusLabel.setText("抬起")
            # 模式键
            if driveManager.mode_btn_is_press(False):
                self.modeStatusLabel.setText("按下")
            else:
                self.modeStatusLabel.setText("抬起")

    def open_osk(self):
        """
        打开软键盘
        使用子线程打开避免卡顿
        """
        oskThread = threading.Thread(target=osk)
        oskThread.start()

    def solidify_config(self):
        """
        固化配置
        """
        # 询问
        msg_box = QMessageBox(
            QMessageBox.Question,
            '固化配置',
            '将修改的配置保存为出厂设置，恢复出厂设置时将使用此配置',
            QMessageBox.No | QMessageBox.Yes
        )
        result = msg_box.exec_()
        # 结果
        if result == QMessageBox.Yes:
            log("固化配置")
            config.solidify_config()
