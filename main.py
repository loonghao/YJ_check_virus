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
from .gui.ui_connector import connector
from .gui.pyside import *


PATH = os.path.abspath(os.path.dirname(__file__))


class MainUi(QtWidgets.QDialog):

    def __init__(self, parent=None):
        super(MainUi, self).__init__(parent)
        self.setWindowTitle("Check Virus")
        self.resize(230, 210)
        self.setup_ui()

    def setup_ui(self):
        image_file = os.path.join(PATH, "icons", "check_virus.png")
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
    virus_gene = [
        "leukocyte",
        "execute",
    ]

    return [
        scriptjob
        for scriptjob in cmds.scriptJob(listJobs=True)
        for virus in virus_gene
        if virus in scriptjob
    ]


def cleanup_virus_script_jobs():
    for script_job in get_virus_script_jobs():
        script_num = int(script_job.split(":", 1)[0])
        cmds.scriptJob(kill=script_num, force=True)


def check_script_files():
    virus_file = ["userSetup.mel",
                  "fuckVirus.py",
                  "fuckVirus.pyc",
                  "vaccine.py",
                  "vaccine.pyc"
                 ]

    script_path = os.path.join(cmds.internalVar(userAppDir=True), "scripts")
    bad_script = list()
    for script in virus_file:
        if script in os.listdir(script_path):
            bad_script.append(os.path.join(script_path, script))

    if bad_script:
        return bad_script

    return False


def check_script_nodes():
    expression_list = cmds.ls(type="script")

    bad_expression = list()
    for expression in expression_list:
        # check uifiguration
        if cmds.objExists("{}.KGMScriptProtector".format(expression)):
            bad_expression.append(expression)
        # check vaccine
        if "_gene" in expression:
            bad_expression.append(expression)

    if bad_expression:
        return bad_expression

    return False


def check_reference_nodes():
    expression_list = cmds.ls(type="script")

    ref_expression = list()
    for expression in expression_list:
        is_ref = cmds.referenceQuery(expression, inr=True)
        if cmds.objExists("{}.KGMScriptProtector".format(expression)) and is_ref:
            ref_expression.append(expression)

        if "_gene" in expression and cmds.referenceQuery(expression, inr=True):
            ref_expression.append(expression)

    if ref_expression:
        return ref_expression

    return False


def check_virus(*args):
    if check_script_files() or check_script_nodes():
        win = MainUi(connector)
        win.show()


def clear_virus(*args):
    bad_script = check_script_files()
    bad_expression = check_script_nodes()
    ref_expression = check_reference_nodes()
    syssst_dir = os.path.join(os.getenv('APPDATA'), 'syssst')

    if bad_script:
        for bad in bad_script:
            if os.path.exists(bad):
                os.remove(bad)
                print("delete {}".format(bad))

    if bad_expression:
        for bad in bad_expression:
            cmds.delete(bad)
            print("delete {}".format(bad))

    if os.path.exists(syssst_dir):
        shutil.rmtree(syssst_dir)
        print("delete {}".format(syssst_dir))

    if ref_expression:
        QtWidgets.QMessageBox.question(None, 'Question!',
                                       u"{} \nCan't Delete, is there a virus in the reference file\n"
                                       u"场景里的reference文件是否有病毒?".format(ref_expression),
                                       buttons=QtWidgets.QMessageBox.Ok
                                       )
        return


def init_run():
    if not OpenMaya.MGlobal.mayaState():
        OpenMaya.MSceneMessage.addCallback(OpenMaya.MSceneMessage.kAfterOpen, check_virus)
        OpenMaya.MSceneMessage.addCallback(OpenMaya.MSceneMessage.kBeforeSave, clear_virus)


def run():
    if not OpenMaya.MGlobal.mayaState():
        check_virus()

