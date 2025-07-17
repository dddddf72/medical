# 高保真的宽度和高度
designWidth = 1280.0
designHeight = 720.0

#屏幕分辨率
screenW = 1280
screenH = 720

def setDesktop(desktop):
    global screenW
    screenW = desktop.screenGeometry().width()
    global screenH
    screenH = desktop.screenGeometry().height()

def scaleSizeW(size):
    scaleWidth = size * screenW / designWidth
    return scaleWidth

def scaleSizeH(size):
    scaleHeight = size * screenH / designHeight
    return scaleHeight

def resolutionW():
    return screenW

def resolutionH():
    return screenH

