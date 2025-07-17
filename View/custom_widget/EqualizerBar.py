import sys
from math import ceil

from PyQt5.QtGui import QPainter

from Utils.Log import log
from Utils.ResolutionTools import scaleSizeW

if 'PyQt5' in sys.modules:
    from PyQt5 import QtCore, QtGui, QtWidgets
    from PyQt5.QtCore import Qt

else:
    from PySide2 import QtCore, QtGui, QtWidgets
    from PySide2.QtCore import Qt

# 原始总格子数
ORIGINAL_CELL = 60
# 映射总格子数
TOTAL_CELL = 100

class EqualizerBar(QtWidgets.QWidget):

    def __init__(self, *args, **kwargs):
        super(EqualizerBar, self).__init__(*args, **kwargs)
        # 进度条个数
        bars = 1
        # 默认配置
        self.set_steps(20, 40)

        self.setSizePolicy(
            QtWidgets.QSizePolicy.MinimumExpanding,
            QtWidgets.QSizePolicy.MinimumExpanding
        )

        # Bar appearance.
        self.n_bars = bars
        self._x_solid_percent = 0.8
        self._y_solid_percent = 0.8
        self._background_color = QtGui.QColor('transparent')
        self._padding = scaleSizeW(25)  # n-pixel gap around edge.

        # Bar behaviour
        # self._timer = None
        # self.setDecayFrequencyMs(100)
        # self._decay = 10

        # Ranges
        self._vmin = 0
        self._vmax = 100

        # Current values are stored in a list.
        self._values = 0.0

        # 进度条方向 0:垂直 1:水平
        self.flow = 0

        # 块中间是否没有间隔 0:没有 1:有，间隔大小 _x_solid_percent
        self.flag = 1

    def set_steps(self, normal, warn):
        """
        设置色块
        对外接口，进度条范围为[0, 100]
        normal + warn < TOTAL_CELL
        :param normal: 正常区域块数
        :param warn: 警告区域块数
        """
        # 映射到原始块数
        normalOriginal = ceil(normal * ORIGINAL_CELL / TOTAL_CELL)
        warnOriginal = ceil(warn * ORIGINAL_CELL / TOTAL_CELL)
        log("正常", "对外：%s；原始：%s" % (normal, normalOriginal))
        log("警告", "对外：%s；原始：%s" % (warn, warnOriginal))
        # 块状原始个数和颜色 60为最佳
        steps = ['#3CB371'] * normalOriginal + ['#EFF821'] * warnOriginal + ['#FF0000'] * (ORIGINAL_CELL - normalOriginal - warnOriginal)

        if isinstance(steps, list):
            # list of colours.
            self.n_steps = len(steps)
            self.steps = steps

        elif isinstance(steps, int):
            # int number of bars, defaults to red.
            self.n_steps = steps
            self.steps = ['red'] * steps

        else:
            raise TypeError('steps must be a list or int')

    def paintEvent(self, e):
        painter = QtGui.QPainter(self)

        brush = QtGui.QBrush()
        brush.setColor(self._background_color)
        # pixmap = QPixmap("img/1.png")
        # brush.setTexture(pixmap)

        brush.setStyle(Qt.SolidPattern)
        rect = QtCore.QRect(0, 0, 0, 0)
        painter.fillRect(rect, brush)

        # Define our canvas.
        # 状态条大小
        d_height = painter.device().height() - (self._padding * 2)
        d_width = painter.device().width() - (self._padding * 2)
        # print('d_height :'+str(painter.device().height())+' d_width :'+str(painter.device().width()))
        # Draw the bars.
        # 单个块的参数
        if self.flow == 0:
            step_y = d_height / self.n_bars
        else:
            step_y = d_height / self.n_steps

        bar_height = step_y * self._y_solid_percent
        bar_height_space = step_y * (1 - self._x_solid_percent) / 2

        if self.flow == 0:
            step_x = d_width / self.n_steps
        else:
            step_x = d_width / self.n_bars

        bar_width = step_x * self._x_solid_percent
        bar_width_space = step_x * (1 - self._y_solid_percent) / 2

        for b in range(self.n_bars):

            # Calculate the y-stop position for this bar, from the value in range.
            pc = (self._values - self._vmin) / (self._vmax - self._vmin)
            # 要画几个块，向上取整
            n_steps_to_draw = ceil(pc * self.n_steps)
            # 画每个块的位置
            for n in range(n_steps_to_draw):
                # pixmap = QPixmap("img/logo.png")
                # brush.setTexture(pixmap)
                brush.setColor(QtGui.QColor(self.steps[n]))

                if self.flow == 0:
                    if self.flag == 0:
                        width = bar_width * 2
                    else:
                        width = bar_width
                    rect = QtCore.QRect(
                        self._padding + ((1 + n) * step_x) + bar_width_space,
                        self._padding + (step_y * b) + bar_height_space,
                        width,
                        bar_height
                    )
                else:
                    rect = QtCore.QRect(
                        self._padding + (step_x * b) + bar_width_space,
                        self._padding + d_height - ((1 + n) * step_y) + bar_height_space,
                        bar_width,
                        bar_height
                    )

                # 圆角
                painter.setRenderHint(QPainter.Antialiasing)  # 抗锯齿
                painter.setBrush(brush)
                painter.drawRoundedRect(rect, 8, 8)

                # 直角
                # painter.fillRect(rect, brush)

        painter.end()

    # def sizeHint(self):
    #     return QtCore.QSize(600, 120)

    def _trigger_refresh(self):
        self.update()

    def setDecay(self, f):
        self._decay = float(f)

    def setDecayFrequencyMs(self, ms):
        if self._timer:
            self._timer.stop()

        if ms:
            self._timer = QtCore.QTimer()
            self._timer.setInterval(ms)
            self._timer.timeout.connect(self._decay_beat)
            self._timer.start()

    def _decay_beat(self):
        # self._values = [
        #     max(0, v - self._decay)
        #     for v in self._values
        # ]
        self.update()  # Redraw new position.

    def setValues(self, v):
        self._values = v
        self.update()

    def values(self):
        return self._values

    def setRange(self, vmin, vmax):
        assert float(vmin) < float(vmax)
        self._vmin, self._vmax = float(vmin), float(vmax)

    def setColor(self, color):
        self.steps = [color] * self._bar.n_steps
        self.update()

    def setColors(self, colors):
        self.n_steps = len(colors)
        self.steps = colors
        self.update()

    def setBarPadding(self, i):
        self._padding = int(i)
        self.update()

    def setBarSolidPercent(self, f):
        self._bar_solid_percent = float(f)
        self.update()

    def setBackgroundColor(self, color):
        self._background_color = QtGui.QColor(color)
        self.update()

    # 进度条方向 0为垂直 1为水平
    def setFlow(self, flow):
        self.flow = flow
        self.update()

    # 块中间是否没有间隔 0:没有 1:有，间隔大小 _x_solid_percent
    def setProgressBarFlag(self, flag):
        self.flag = flag
        self.update()
