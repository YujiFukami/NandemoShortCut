"""
startup_manager.py - Windows スタートアップ登録管理

タスク スケジューラを優先して使用し、必要に応じてレガシーな
スタートアップフォルダ登録も削除する。
"""

import os
import subprocess
import sys
import ctypes
from ctypes import wintypes


APP_NAME = "NandemoShortcut"
STARTUP_SCRIPT_NAME = f"{APP_NAME}.bat"
STARTUP_TASK_NAME = APP_NAME


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


def _get_task_name():
    return STARTUP_TASK_NAME


def _run_schtasks(args):
    return subprocess.run(
        ["schtasks", *args],
        capture_output=True,
        text=True,
        encoding="cp932",
        errors="replace",
        check=False,
    )


def _run_schtasks_elevated(args):
    executable = os.path.join(os.environ.get("WINDIR", r"C:\Windows"), "System32", "schtasks.exe")
    if not os.path.exists(executable):
        raise OSError(f"昇格実行に必要なファイルが見つかりません: {executable}")

    parameters = subprocess.list2cmdline(args)
    SEE_MASK_NOCLOSEPROCESS = 0x00000040
    INFINITE = 0xFFFFFFFF

    class SHELLEXECUTEINFO(ctypes.Structure):
        _fields_ = [
            ("cbSize", wintypes.DWORD),
            ("fMask", wintypes.ULONG),
            ("hwnd", wintypes.HWND),
            ("lpVerb", wintypes.LPCWSTR),
            ("lpFile", wintypes.LPCWSTR),
            ("lpParameters", wintypes.LPCWSTR),
            ("lpDirectory", wintypes.LPCWSTR),
            ("nShow", ctypes.c_int),
            ("hInstApp", wintypes.HINSTANCE),
            ("lpIDList", wintypes.LPVOID),
            ("lpClass", wintypes.LPCWSTR),
            ("hkeyClass", wintypes.HKEY),
            ("dwHotKey", wintypes.DWORD),
            ("hIconOrMonitor", wintypes.HANDLE),
            ("hProcess", wintypes.HANDLE),
        ]

    info = SHELLEXECUTEINFO()
    info.cbSize = ctypes.sizeof(SHELLEXECUTEINFO)
    info.fMask = SEE_MASK_NOCLOSEPROCESS
    info.hwnd = None
    info.lpVerb = "runas"
    info.lpFile = executable
    info.lpParameters = parameters
    info.lpDirectory = None
    info.nShow = 1

    shell32 = ctypes.windll.shell32
    kernel32 = ctypes.windll.kernel32

    success = shell32.ShellExecuteExW(ctypes.byref(info))
    if not success:
        rc = kernel32.GetLastError()
        messages = {
            2: "ファイルが見つかりません。",
            3: "パスが見つかりません。",
            5: "アクセスが拒否されました。",
            1223: "管理者権限の確認がキャンセルされました。",
        }
        detail = messages.get(rc, f"ShellExecuteW failed: {rc}")
        return subprocess.CompletedProcess(args, 1, "", detail)

    exit_code = wintypes.DWORD()
    kernel32.WaitForSingleObject(info.hProcess, INFINITE)
    kernel32.GetExitCodeProcess(info.hProcess, ctypes.byref(exit_code))
    kernel32.CloseHandle(info.hProcess)
    return subprocess.CompletedProcess(args, exit_code.value, "", "")


def _task_exists():
    result = _run_schtasks(["/Query", "/TN", _get_task_name()])
    return result.returncode == 0


def _delete_legacy_startup_script():
    script_path = get_startup_script_path()
    if os.path.exists(script_path):
        os.remove(script_path)
    return script_path


def is_startup_enabled():
    return _task_exists() or os.path.exists(get_startup_script_path())


def enable_startup():
    command = _get_launcher_command()
    args = [
        "/Create",
        "/TN", _get_task_name(),
        "/SC", "ONLOGON",
        "/RL", "HIGHEST",
        "/F",
        "/TR", command,
    ]
    result = _run_schtasks(args)
    detail = (result.stderr or result.stdout).strip()
    if result.returncode != 0 and "アクセスが拒否" in detail:
        result = _run_schtasks_elevated(args)
        detail = (result.stderr or result.stdout).strip()
    if result.returncode != 0:
        raise OSError(f"タスク スケジューラへの登録に失敗しました: {detail}")

    _delete_legacy_startup_script()
    return f"タスク スケジューラ: {_get_task_name()} (最上位の特権で実行)"


def disable_startup():
    legacy_path = _delete_legacy_startup_script()
    if _task_exists():
        result = _run_schtasks(["/Delete", "/TN", _get_task_name(), "/F"])
        if result.returncode != 0:
            detail = (result.stderr or result.stdout).strip()
            raise OSError(f"タスク スケジューラの解除に失敗しました: {detail}")
        return f"タスク スケジューラ: {_get_task_name()}"
    return legacy_path
