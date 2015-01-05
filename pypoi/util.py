import os
import sys


def resource_path(relative):
    """
    Resolve path to resource (for supporting PyInstaller).

    When PyInstaller is executed with --onefile option, resources are put in a
    temporary dir and scripts need to use the info to access resources.

    ref: http://stackoverflow.com/questions/13946650/pyinstaller-2-0-bundle-file-as-onefile
    """
    if hasattr(sys, '_MEIPASS'):
        root = os.path.join(sys._MEIPASS, 'pypoi')
    else:
        root = os.path.abspath(os.path.dirname(__file__))

    return os.path.join(root, relative)
