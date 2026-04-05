"""
main.py - なんでもショートカット エントリーポイント

各モジュールを初期化・統合し、アプリケーションを起動する。
"""

import sys
import os
import tkinter as tk
import threading
import ctypes

# モジュールのインポート
from config_manager import ConfigManager
from action_executor import ActionExecutor
from hotkey_listener import HotkeyListener
from overlay_window import OverlayWindow
from settings_window import SettingsWindow
from tray_icon import TrayIcon


_SINGLE_INSTANCE_MUTEX_NAME = "Local\\NandemoShortcut_SingleInstance"


class SingleInstanceGuard:
    """Windows の名前付きミューテックスで単一起動を保証する"""

    def __init__(self, mutex_name):
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


class NandemoShortcutApp:
    """なんでもショートカット メインアプリケーション"""

    def __init__(self):
        # tkinter ルートウィンドウ（非表示）
        self.root = tk.Tk()
        self.root.withdraw()  # メインウィンドウを隠す
        self.root.title("なんでもショートカット")

        # 各モジュールの初期化
        self.config = ConfigManager()
        self.executor = ActionExecutor()

        self.overlay = OverlayWindow(
            self.root,
            self.config,
            self.executor,
            on_complete=self._on_action_complete,
            on_open_settings=self._show_settings,
        )

        self.settings = SettingsWindow(
            self.root,
            self.config,
            on_config_changed=self._on_config_changed,
        )

        self.hotkey = HotkeyListener(
            activation_key=self.config.activation_key,
            on_activate=self._on_hotkey_activate,
        )

        self.tray = TrayIcon(
            on_settings=self._show_settings,
            on_quit=self._quit_app,
        )

    def run(self):
        """アプリケーションを起動"""
        print("なんでもショートカット を起動しています...")
        print(f"呼び出しキー: {self.config.activation_key}")
        print(f"登録アクション数: {len(self.config.get_all_actions_flat())}")

        # ホットキー監視を開始
        self.hotkey.start()

        # システムトレイアイコンを表示
        self.tray.start()

        print("起動完了！システムトレイに常駐しています。")
        print(f"{self.config.activation_key.upper()} キーを押してアクションを呼び出してください。")

        # tkinter メインループ
        try:
            self.root.mainloop()
        except KeyboardInterrupt:
            self._quit_app()

    def _on_hotkey_activate(self):
        """ホットキーが押された時"""
        # tkinterのメインスレッドで実行
        self.root.after(0, self._show_overlay)

    def _show_overlay(self):
        """オーバーレイを表示"""
        if not self.overlay.is_visible():
            self.overlay.show()

    def _show_settings(self):
        """設定ウィンドウを表示"""
        self.root.after(0, self.settings.show)

    def _on_action_complete(self, success, message):
        """アクション完了時"""
        status = "✓" if success else "✗"
        print(f"  {status} {message}")

    def _on_config_changed(self):
        """設定変更時"""
        # ホットキーを更新
        self.hotkey.update_activation_key(self.config.activation_key)
        print(f"設定が更新されました。呼び出しキー: {self.config.activation_key}")

    def _quit_app(self):
        """アプリケーションを終了"""
        print("なんでもショートカット を終了しています...")
        self.hotkey.stop()
        self.tray.stop()
        self.root.after(0, self.root.destroy)


def main():
    """エントリーポイント"""
    instance_guard = SingleInstanceGuard(_SINGLE_INSTANCE_MUTEX_NAME)
    if not instance_guard.acquire():
        print("なんでもショートカット は既に起動しています。")
        return

    # 管理者権限チェック（グローバルホットキーに必要な場合がある）
    try:
        is_admin = ctypes.windll.shell32.IsUserAnAdmin()
        if not is_admin:
            print("注意: 管理者権限で実行すると、一部のアプリケーション上でもホットキーが動作します。")
    except Exception:
        pass

    try:
        app = NandemoShortcutApp()
        app.run()
    finally:
        instance_guard.release()


if __name__ == "__main__":
    main()
