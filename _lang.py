# -*- conding: utf-8 -*-

import os
import re
import json
import shutil
import winreg

LANG_DIR: str = "./lang/"
_json: dict = {}


def get_system_language() -> str:
    try:
        with winreg.OpenKey(winreg.HKEY_CURRENT_USER,
                            r"Control Panel\International") as key:
            language = winreg.QueryValueEx(key, "LocaleName")[0]
            return language.lower().replace('_', '-')
    except:
        return "en-us"


def get_app_language_list() -> list[str]:
    languages: list[str] = []
    for _ in os.listdir(LANG_DIR):
        if _.endswith(".json") and \
                re.match(r"^[a-z]{1,2}-[a-z]{1,2}.json$", _) == _:
            languages.append(_)

    return languages


def get_language_json(language: str) -> dict:
    with open(f"{LANG_DIR}{language}.json", encoding="utf-8") as file:
        return json.load(file)


def add_language_json(language_json_path: str) -> None:
    if not os.path.isfile(language_json_path) or \
            not language_json_path.endswith(".json") \
            or re.match(r"^[a-z]{1,2}-[a-z]{1,2}.json$",
                        os.path.basename(language_json_path)) != \
            language_json_path:
        shutil.copy(language_json_path, LANG_DIR)
    else:
        raise RuntimeError("The Language File Name Is Not Legal 语言文件名不合法 語言檔名不合法 \
言語ファイル名が不正")


def init_i18n(language_json: dict) -> None:
    global _json
    _json = language_json


def t(x: str) -> str:
    if _json is None:
        raise RuntimeError("Not Initialized 未初始化 沒有初始化 初期化されていません")
    return _json[x]


if __name__ == "__main__":
    raise RuntimeError("Try Running The Module File 尝试运行模块文件 嘗試運行模組檔 \
モジュールファイルを実行してみてください")
