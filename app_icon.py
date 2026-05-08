"""
app_icon.py - アプリ共通アイコン
"""

import os
import sys
import tkinter as tk


ICON_FILE_NAME = "NandemoShortcut.ico"


def get_resource_path(file_name):
    """開発時とPyInstaller実行時の両方でリソースパスを取得する。"""
    base_dir = getattr(sys, "_MEIPASS", os.path.dirname(os.path.abspath(__file__)))
    return os.path.join(base_dir, file_name)


def get_app_icon_path():
    return get_resource_path(ICON_FILE_NAME)


def apply_window_icon(window):
    """tkinterウィンドウにアプリアイコンを設定する。"""
    icon_path = get_app_icon_path()
    if not os.path.exists(icon_path):
        return
    try:
        window.iconbitmap(icon_path)
    except (tk.TclError, OSError):
        pass
