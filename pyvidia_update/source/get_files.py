import sys


def get_packaged_files_path():
    """Location of relative paths"""
    if getattr(sys, "frozen", False):
        path = sys._MEIPASS  # noqa
    else:
        path = "."

    return path
