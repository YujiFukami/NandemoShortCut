"""
startup_manager.py - Windows スタートアップ登録管理

スタートアップフォルダに起動用バッチファイルを作成・削除する。
"""

import os
import sys


APP_NAME = "NandemoShortcut"
STARTUP_SCRIPT_NAME = f"{APP_NAME}.bat"


def _get_startup_dir():
    appdata = os.environ.get("APPDATA", "")
    return os.path.join(
        appdata,
        "Microsoft",
        "Windows",
        "Start Menu",
        "Programs",
        "Startup",
    )


def _get_launcher_command():
    if getattr(sys, "frozen", False):
        return f'"{sys.executable}"'

    python_exe = sys.executable
    main_py = os.path.join(os.path.dirname(os.path.abspath(__file__)), "main.py")
    return f'"{python_exe}" "{main_py}"'


def get_startup_script_path():
    return os.path.join(_get_startup_dir(), STARTUP_SCRIPT_NAME)


def is_startup_enabled():
    return os.path.exists(get_startup_script_path())


def enable_startup():
    startup_dir = _get_startup_dir()
    if not os.path.isdir(startup_dir):
        raise OSError(f"スタートアップフォルダが見つかりません: {startup_dir}")

    script_path = get_startup_script_path()
    command = _get_launcher_command()
    content = "@echo off\nstart \"\" " + command + "\n"

    with open(script_path, "w", encoding="utf-8", newline="\n") as f:
        f.write(content)

    return script_path


def disable_startup():
    script_path = get_startup_script_path()
    if os.path.exists(script_path):
        os.remove(script_path)
    return script_path
