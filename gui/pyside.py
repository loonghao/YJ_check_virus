# coding:utf-8


try:
	from PySide2 import QtGui
	from PySide2 import QtWidgets
	from shiboken2 import wrapInstance
except:
	from PySide6 import QtGui
	from PySide6 import QtWidgets
	from shiboken6 import wrapInstance
