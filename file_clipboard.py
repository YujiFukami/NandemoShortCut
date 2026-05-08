"""
file_clipboard.py - Windows クリップボードへファイルを登録
"""

import ctypes
from ctypes import wintypes


CF_HDROP = 15
GMEM_MOVEABLE = 0x0002
GMEM_ZEROINIT = 0x0040

kernel32 = ctypes.windll.kernel32
user32 = ctypes.windll.user32

kernel32.GlobalAlloc.argtypes = (wintypes.UINT, ctypes.c_size_t)
kernel32.GlobalAlloc.restype = wintypes.HGLOBAL
kernel32.GlobalLock.argtypes = (wintypes.HGLOBAL,)
kernel32.GlobalLock.restype = ctypes.c_void_p
kernel32.GlobalUnlock.argtypes = (wintypes.HGLOBAL,)
kernel32.GlobalUnlock.restype = wintypes.BOOL
kernel32.GlobalFree.argtypes = (wintypes.HGLOBAL,)
kernel32.GlobalFree.restype = wintypes.HGLOBAL

user32.OpenClipboard.argtypes = (wintypes.HWND,)
user32.OpenClipboard.restype = wintypes.BOOL
user32.EmptyClipboard.argtypes = ()
user32.EmptyClipboard.restype = wintypes.BOOL
user32.SetClipboardData.argtypes = (wintypes.UINT, wintypes.HANDLE)
user32.SetClipboardData.restype = wintypes.HANDLE
user32.CloseClipboard.argtypes = ()
user32.CloseClipboard.restype = wintypes.BOOL


class DROPFILES(ctypes.Structure):
    _fields_ = [
        ("pFiles", wintypes.DWORD),
        ("pt_x", wintypes.LONG),
        ("pt_y", wintypes.LONG),
        ("fNC", wintypes.BOOL),
        ("fWide", wintypes.BOOL),
    ]


def copy_files_to_clipboard(paths):
    """ファイル一覧を Windows クリップボードへコピーする。"""
    normalized_paths = [str(path) for path in paths if path]
    if not normalized_paths:
        raise ValueError("コピーするファイルが指定されていません")

    payload = _build_dropfiles_payload(normalized_paths)
    handle = _allocate_global_memory(payload)

    if not user32.OpenClipboard(None):
        kernel32.GlobalFree(handle)
        raise OSError("クリップボードを開けませんでした")

    try:
        if not user32.EmptyClipboard():
            raise OSError("クリップボードを空にできませんでした")
        if not user32.SetClipboardData(CF_HDROP, handle):
            raise OSError("ファイルをクリップボードに設定できませんでした")
        handle = None
    finally:
        user32.CloseClipboard()
        if handle:
            kernel32.GlobalFree(handle)


def _build_dropfiles_payload(paths):
    file_list = ("\0".join(paths) + "\0\0").encode("utf-16le")
    header = DROPFILES()
    header.pFiles = ctypes.sizeof(DROPFILES)
    header.pt_x = 0
    header.pt_y = 0
    header.fNC = False
    header.fWide = True
    return bytes(header) + file_list


def _allocate_global_memory(payload):
    size = len(payload)
    handle = kernel32.GlobalAlloc(GMEM_MOVEABLE | GMEM_ZEROINIT, size)
    if not handle:
        raise MemoryError("クリップボード用メモリを確保できませんでした")

    locked = kernel32.GlobalLock(handle)
    if not locked:
        kernel32.GlobalFree(handle)
        raise MemoryError("クリップボード用メモリをロックできませんでした")

    try:
        ctypes.memmove(locked, payload, size)
    finally:
        kernel32.GlobalUnlock(handle)

    return handle
