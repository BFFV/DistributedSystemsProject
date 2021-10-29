import os
import sys


def fix_imports():
    this_file_path = os.path.join(os.getcwd(), os_py_path())
    root_path = '/'.join(this_file_path.rstrip('/').split('/')[:-1])
    new_path = os.path.join(root_path, 'libs')
    sys.path.insert(0, new_path)


def os_py_path():
    return '/'.join(sys.argv[0].split('/')[:-1])
