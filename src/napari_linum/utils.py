from os import path
import re


def get_name(fpath):
    return path.basename(fpath).split(".")[0]


def get_extension(fpath):
    return str(path.basename(fpath).split(".")[-1]).lower()


def replace_text_in_parenthesis(text: str, replace: str) -> str:
    return re.sub(r'\(.*?\)', f'({replace})', text)

