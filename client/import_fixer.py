import os
import sys


def fix_imports():
    new_path = os.path.abspath(os.path.join("libs"))
    sys.path.append(new_path)
