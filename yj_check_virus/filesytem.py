import os
import maya.cmds as cmds
import shutil


def this_root():
    return os.path.abspath(os.path.dirname(__file__))


def get_icon(name):
    return os.path.join(this_root(), "icons", name)


def get_local_script_path():
    return os.path.join(cmds.internalVar(userAppDir=True), "scripts")


def list_scripts_nodes():
    return cmds.ls(type="script")


def get_syssst_dir():
    return os.path.join(os.getenv('APPDATA'), 'syssst')


def safe_remove_file(file_path):
    try:
        os.remove(file_path)
        print("delete {}".format(file_path))
    except (IOError, PermissionError):
        pass


def safe_rmtree(path):
    try:
        shutil.rmtree(path)
        print("delete {}".format(path))
    except (IOError, PermissionError):
        pass
