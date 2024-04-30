# coding:utf-8
"""
------------------------------------------------------------------------------------------

@author: Liujingjing
@email : yjjjj@live.cn

Release Date: 2024.04.29
------------------------------------------------------------------------------------------
"""

import os
import shutil

from maya import cmds
from maya import OpenMaya
from yj_check_virus.gui.ui_connector import connector
from yj_check_virus.gui.pyside import QtWidgets
from yj_check_virus.gui.pyside import QtGui
from yj_check_virus.constants import VIRUS_FILES
from yj_check_virus.constants import VIRUS_NAMES
from yj_check_virus.filesytem import get_icon
from yj_check_virus.filesytem import get_local_script_path
from yj_check_virus.filesytem import list_scripts_nodes
from yj_check_virus.filesytem import get_syssst_dir
from yj_check_virus.filesytem import safe_remove_file
from yj_check_virus.filesytem import safe_rmtree


class MainUi(QtWidgets.QDialog):

    def __init__(self, parent=None):
        super(MainUi, self).__init__(parent)
        self.setWindowTitle("Check Virus")
        self.resize(230, 210)
        self.setup_ui()

    def setup_ui(self):
        image_file = get_icon("check_virus.png")
        pixmap = QtGui.QPixmap(image_file)
        self.text_label = QtWidgets.QLabel()
        self.text_label.setStyleSheet("font-size:16px; border:2px solid #343434")
        self.text_label.setHidden(True)
        self.image_label = QtWidgets.QLabel()
        self.image_label.setPixmap(pixmap)
        clear_btn = QtWidgets.QPushButton(u"清除病毒")
        clear_btn.clicked.connect(self.clear_vaccine_click)

        btn_layout = QtWidgets.QHBoxLayout()
        btn_layout.addWidget(clear_btn)

        main_layout = QtWidgets.QVBoxLayout(self)
        main_layout.addWidget(self.text_label)
        main_layout.addWidget(self.image_label)
        main_layout.addLayout(btn_layout)

    def clear_vaccine_click(self):
        clear_virus()
        cleanup_virus_script_jobs()
        self.image_label.setHidden(True)
        self.text_label.setHidden(False)
        self.text_label.setText(u"Virus cleared(病毒已清除)")


def get_virus_script_jobs():
    """Traverse the list of virus script job name.
    Returns:
        list: Malicious virus script job name.
    """
    return [
        scriptjob
        for scriptjob in cmds.scriptJob(listJobs=True)
        for virus in VIRUS_NAMES
        if virus in scriptjob
    ]


def cleanup_virus_script_jobs():
    for script_job in get_virus_script_jobs():
        script_num = int(script_job.split(":", 1)[0])
        cmds.scriptJob(kill=script_num, force=True)


def check_script_files():
    script_path = get_local_script_path()
    bad_script = []
    for script in VIRUS_FILES:
        if script in os.listdir(script_path):
            bad_script.append(os.path.join(script_path, script))

    return bad_script


def check_script_nodes():
    expression_list = list_scripts_nodes()

    bad_expression = []
    for expression in expression_list:
        # check uifiguration
        if cmds.objExists("{}.KGMScriptProtector".format(expression)):
            bad_expression.append(expression)
        # check vaccine
        if "_gene" in expression:
            bad_expression.append(expression)

    return bad_expression


def check_reference_nodes():
    expression_list = list_scripts_nodes()

    ref_expression = []
    for expression in expression_list:
        is_ref = cmds.referenceQuery(expression, inr=True)
        if cmds.objExists("{}.KGMScriptProtector".format(expression)) and is_ref:
            ref_expression.append(expression)

        if "_gene" in expression and cmds.referenceQuery(expression, inr=True):
            ref_expression.append(expression)

    if ref_expression:
        return ref_expression

    return False


def check_virus(*args, **kwargs):
    if check_script_files() or check_script_nodes():
        win = MainUi(connector)
        win.show()


def clear_virus(*args, **kwargs):
    bad_scripts = check_script_files()
    bad_expressions = check_script_nodes()
    ref_expression = check_reference_nodes()
    syssst_dir = get_syssst_dir()
    for bad_script in bad_scripts:
        safe_remove_file(bad_script)
    for bad_expression in bad_expressions:
        cmds.delete(bad_expression)
        print("delete {}".format(bad_expression))
    safe_rmtree(syssst_dir)
    if ref_expression:
        QtWidgets.QMessageBox.question(None, 'Question!',
                                       u"{} \nCan't Delete, is there a virus in the reference file\n"
                                       u"场景里的reference文件是否有病毒?".format(ref_expression),
                                       buttons=QtWidgets.QMessageBox.Ok
                                       )
        return


def setup_callback():
    if not OpenMaya.MGlobal.mayaState():
        OpenMaya.MSceneMessage.addCallback(OpenMaya.MSceneMessage.kAfterOpen, check_virus)
        OpenMaya.MSceneMessage.addCallback(OpenMaya.MSceneMessage.kAfterImport, check_virus)
        OpenMaya.MSceneMessage.addCallback(OpenMaya.MSceneMessage.kAfterImportReference, check_virus)
        OpenMaya.MSceneMessage.addCallback(OpenMaya.MSceneMessage.kBeforeSave, clear_virus)
        OpenMaya.MSceneMessage.addCallback(OpenMaya.MSceneMessage.kMayaExiting, clear_virus)


def run():
    if not OpenMaya.MGlobal.mayaState():
        check_virus()
