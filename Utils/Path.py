import os
import sys

"""
项目运行根目录

若使用相对路径，文件被引用时将从引用者所在目录为起点，易引起混乱
因此所有资源的定位使用此路径确定绝对路径使用

整个项目如果被打包成一个exe文件，运行时将被解压到临时文件夹中
此时资源文件需要使用此临时文件夹为根目录

若项目打包成文件夹，将不会使用临时文件夹，本地址即项目实际存在目录
"""
rootPath = os.path.abspath(os.path.dirname(os.path.dirname(__file__))).replace("\\", "/")

"""
存储目录（即项目实际存在目录）

为防止使用了临时文件夹导致需要持久化存储的文件无法找到
所有需要持久化 存储的文件使用此存储目录为目标存储地点
"""
storagePath = os.path.abspath(os.path.dirname(sys.argv[0])).replace("\\", "/")
