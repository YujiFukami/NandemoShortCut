"""
explorer_utils.py - Explorerウィンドウのアクティブパス取得

Windows Shell COM経由でアクティブなExplorerウィンドウのパスを取得する。
"""

import os


def get_active_explorer_path():
    """アクティブなExplorerウィンドウの現在のパスを取得する。

    Returns:
        str or None: Explorerのパス。取得できない場合はNone。
    """
    try:
        import comtypes
        import comtypes.client

        # Shell.Application COM オブジェクトを取得
        shell = comtypes.client.CreateObject("Shell.Application")
        windows = shell.Windows()

        if windows.Count == 0:
            return None

        # フォアグラウンドのExplorerウィンドウを探す
        import ctypes
        foreground_hwnd = ctypes.windll.user32.GetForegroundWindow()

        for i in range(windows.Count):
            try:
                window = windows.Item(i)
                if window is None:
                    continue

                # ウィンドウハンドルを比較
                hwnd = window.HWND
                if hwnd == foreground_hwnd:
                    # LocationURL からパスを取得
                    location_url = window.LocationURL
                    if location_url:
                        # file:///C:/... 形式をパスに変換
                        path = _url_to_path(location_url)
                        if path and os.path.isdir(path):
                            return path
            except Exception:
                continue

        # フォアグラウンドで見つからない場合は最初のExplorerを使用
        for i in range(windows.Count):
            try:
                window = windows.Item(i)
                if window is None:
                    continue
                location_url = window.LocationURL
                if location_url:
                    path = _url_to_path(location_url)
                    if path and os.path.isdir(path):
                        return path
            except Exception:
                continue

    except Exception as e:
        print(f"Explorer パスの取得に失敗: {e}")

    return None


def _url_to_path(url):
    """file:///形式のURLをWindowsパスに変換する。

    Args:
        url: file:///C:/Users/... 形式の文字列

    Returns:
        str: Windowsパス（例: C:\\Users\\...）
    """
    from urllib.parse import unquote

    if url.startswith("file:///"):
        path = url[8:]  # "file:///" を除去
        path = unquote(path)  # URLエンコードをデコード
        path = path.replace("/", "\\")  # スラッシュをバックスラッシュに
        return path
    return None


def create_folder_in_path(base_path, folder_name):
    """指定パスにフォルダを作成する。

    Args:
        base_path: 作成先のディレクトリパス
        folder_name: 作成するフォルダ名

    Returns:
        tuple: (成功フラグ, メッセージ)
    """
    if not base_path or not os.path.isdir(base_path):
        return False, f"パスが無効です: {base_path}"

    new_path = os.path.join(base_path, folder_name)

    if os.path.exists(new_path):
        return False, f"フォルダは既に存在します: {folder_name}"

    try:
        os.makedirs(new_path)
        return True, f"フォルダを作成しました: {folder_name}"
    except OSError as e:
        return False, f"フォルダ作成に失敗: {e}"
