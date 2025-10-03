import os

def list_folder(path=None):
    if path is None:
        return os.listdir()
    return os.listdir(path)

def back(path=None):
    return
