# coding:utf-8

from .pyside import *
import maya.OpenMayaUI as omui
from maya import cmds


if cmds.about(version=True) < '2022':
    connector = wrapInstance(long(omui.MQtUtil.mainWindow()), QtWidgets.QDialog)
else:
    connector = wrapInstance(int(omui.MQtUtil.mainWindow()), QtWidgets.QDialog)
