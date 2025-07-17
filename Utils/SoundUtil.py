import threading

import pygame
import win32api

from Config.Config import config
from Utils.Log import log
from Utils.Path import rootPath

BEEP_MP3 = rootPath + "/Utils/Beep.mp3"
DI_MP3 = rootPath + "/Utils/Di.mp3"


class SoundUtil(object):
    """
    声音工具
    """
    # 本类初始化列表
    __instanceList = []

    def __init__(self, file_path, time):
        """
        :param file_path: 声音文件地址
        :param time: 播放时长
        """
        # 参数初始化
        self.__filePath = file_path
        self.__time = time

        # 初始化播放器
        pygame.mixer.init()
        # sound 对象
        log("SoundUtil file path", self.__filePath)
        self.__sound = pygame.mixer.Sound(self.__filePath)
        self.__sound.set_volume(config.volume)

        # 是否正在瞬间播放中
        self.__playingSecond = False

        # 加入本类初始化列表
        SoundUtil.__instanceList.append(self)

    def __stop_second(self):
        """
        停止瞬间播放
        """
        self.__playingSecond = False
        self.__sound.stop()

    def play_second(self):
        """
        开始瞬间播放
        """
        # 正在瞬间播放中，不允许播放
        if self.__playingSecond:
            return

        # 播放，重复播放
        self.__playingSecond = True
        self.__sound.play()
        threading.Timer(self.__time, self.__stop_second).start()

    @staticmethod
    def set_volume(volume):
        """
        设置音量
        静态方法
        :param volume: 音量
        """
        log("SoundUtil set_volume", volume)
        for instance in SoundUtil.__instanceList:
            instance.__sound.set_volume(volume)

    @staticmethod
    def system_volume_max():
        """
        初始化系统音量最大值
        参考：https://www.zhihu.com/question/50565812?ivk_sa=1024320u
        使用子线程运行 win32api.SendMessage 该子线程将一直存活到应用结束
        """
        # 仅在 model and view 非 debug 时配置。该配置短期内会影响系统流畅性，不利于调试
        if not config.model_is_debug and not config.view_is_debug:
            log("初始化系统音量最大值")
            win32api.SendMessage(-1, 0x319, 0x30292, 0x0a * 0x10000)
