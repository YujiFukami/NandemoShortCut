"""
launch_protocol.py - 起動経路と既存インスタンス通知の共通処理
"""

import ctypes
import os
import subprocess
import sys


APP_NAME = "NandemoShortcut"
MAIN_EXE_NAME = f"{APP_NAME}.exe"
LAUNCHER_EXE_NAME = f"{APP_NAME}Launcher.exe"
SINGLE_INSTANCE_MUTEX_NAME = "Local\\NandemoShortcut_SingleInstance"
SHOW_MAIN_EVENT_NAME = "Local\\NandemoShortcut_ShowMain"


class SingleInstanceGuard:
    """Windows の名前付きミューテックスで単一起動を保証する"""

    def __init__(self, mutex_name=SINGLE_INSTANCE_MUTEX_NAME):
        self.mutex_name = mutex_name
        self.handle = None

    def acquire(self):
        kernel32 = ctypes.windll.kernel32
        self.handle = kernel32.CreateMutexW(None, False, self.mutex_name)
        if not self.handle:
            return True
        return kernel32.GetLastError() != 183

    def release(self):
        if self.handle:
            ctypes.windll.kernel32.CloseHandle(self.handle)
            self.handle = None


class MainWindowSignal:
    """別プロセスからメイン画面表示を通知する Windows イベント"""

    EVENT_MODIFY_STATE = 0x0002
    SYNCHRONIZE = 0x00100000
    WAIT_OBJECT_0 = 0

    def __init__(self, event_name=SHOW_MAIN_EVENT_NAME):
        self.event_name = event_name
        self.handle = None

    def create(self):
        kernel32 = ctypes.windll.kernel32
        self.handle = kernel32.CreateEventW(None, False, False, self.event_name)
        return bool(self.handle)

    def is_signaled(self):
        if not self.handle:
            return False
        result = ctypes.windll.kernel32.WaitForSingleObject(self.handle, 0)
        return result == self.WAIT_OBJECT_0

    def signal_existing_instance(self):
        kernel32 = ctypes.windll.kernel32
        handle = kernel32.OpenEventW(self.EVENT_MODIFY_STATE | self.SYNCHRONIZE, False, self.event_name)
        if not handle:
            return False
        try:
            return bool(kernel32.SetEvent(handle))
        finally:
            kernel32.CloseHandle(handle)

    def close(self):
        if self.handle:
            ctypes.windll.kernel32.CloseHandle(self.handle)
            self.handle = None


def is_frozen():
    return bool(getattr(sys, "frozen", False))


def get_runtime_dir():
    if is_frozen():
        return os.path.dirname(sys.executable)
    return os.path.dirname(os.path.abspath(__file__))


def get_main_entry_script():
    return os.path.join(get_runtime_dir(), "main.py")


def get_launcher_entry_script():
    return os.path.join(get_runtime_dir(), "launcher.py")


def get_main_executable_path():
    if is_frozen():
        current_name = os.path.basename(sys.executable).lower()
        if current_name == MAIN_EXE_NAME.lower():
            return sys.executable
        return os.path.join(get_runtime_dir(), MAIN_EXE_NAME)
    return sys.executable


def get_launcher_executable_path():
    if is_frozen():
        current_name = os.path.basename(sys.executable).lower()
        if current_name == LAUNCHER_EXE_NAME.lower():
            return sys.executable
        return os.path.join(get_runtime_dir(), LAUNCHER_EXE_NAME)
    return sys.executable


def get_main_launch_spec(background=False):
    arguments = []
    if background:
        arguments.append("--background")

    if is_frozen():
        return {
            "target_path": get_main_executable_path(),
            "arguments": " ".join(arguments),
            "working_directory": get_runtime_dir(),
            "icon_location": get_main_executable_path(),
        }

    argv = [f'"{get_main_entry_script()}"']
    argv.extend(arguments)
    return {
        "target_path": sys.executable,
        "arguments": " ".join(argv),
        "working_directory": get_runtime_dir(),
        "icon_location": sys.executable,
    }


def get_launcher_launch_spec():
    if is_frozen():
        return {
            "target_path": get_launcher_executable_path(),
            "arguments": "",
            "working_directory": get_runtime_dir(),
            "icon_location": get_main_executable_path(),
        }

    return {
        "target_path": sys.executable,
        "arguments": f'"{get_launcher_entry_script()}"',
        "working_directory": get_runtime_dir(),
        "icon_location": sys.executable,
    }


def start_main_process(background=False):
    if is_frozen():
        command = [get_main_executable_path()]
    else:
        command = [sys.executable, get_main_entry_script()]

    if background:
        command.append("--background")

    creation_flags = getattr(subprocess, "CREATE_NO_WINDOW", 0)
    return subprocess.Popen(
        command,
        cwd=get_runtime_dir(),
        close_fds=False,
        creationflags=creation_flags,
    )
