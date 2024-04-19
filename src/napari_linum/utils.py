from os import path

def get_name(fpath):
    return path.basename(fpath).split(".")[0]

def get_extension(fpath):
    return str(path.basename(fpath).split(".")[-1]).lower()

