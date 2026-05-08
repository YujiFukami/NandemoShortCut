"""
main.py - なんでもショートカット エントリーポイント

各モジュールを初期化・統合し、アプリケーションを起動する。
"""

import sys
import tkinter as tk

# モジュールのインポート
from config_manager import ConfigManager
from action_executor import ActionExecutor
from launch_protocol import MainWindowSignal, SingleInstanceGuard
from overlay_window import OverlayWindow
from settings_window import SettingsWindow
from tray_icon import TrayIcon

class NandemoShortcutApp:
    """なんでもショートカット メインアプリケーション"""

    def __init__(self, show_main_on_start=False):
        # tkinter ルートウィンドウ（非表示）
        self.root = tk.Tk()
        self.root.withdraw()  # メインウィンドウを隠す
        self.root.title("なんでもショートカット")
        self.show_main_on_start = show_main_on_start
        self.show_main_signal = MainWindowSignal()
        self.show_main_signal.create()

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

        self.tray = TrayIcon(
            on_open_main=self._show_main_window,
            on_settings=self._show_settings,
            on_quit=self._quit_app,
        )

    def run(self):
        """アプリケーションを起動"""
        print("なんでもショートカット を起動しています...")
        print(f"登録アクション数: {len(self.config.get_all_actions_flat())}")

        # システムトレイアイコンを表示
        self.tray.start()

        print("起動完了！システムトレイに常駐しています。")
        print("EXE の再実行またはトレイメニューからメイン画面を開けます。")
        self.root.after(0, self._finish_startup)

        # tkinter メインループ
        try:
            self.root.mainloop()
        except KeyboardInterrupt:
            self._quit_app()

    def _finish_startup(self):
        if self.show_main_on_start:
            self._show_main_window()
        self._poll_show_main_signal()

    def _poll_show_main_signal(self):
        if self.show_main_signal.is_signaled():
            self._show_main_window()
        self.root.after(200, self._poll_show_main_signal)

    def _show_main_window(self):
        """メイン画面を表示"""
        if not self.overlay.is_visible():
            self.overlay.show()
            return
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
        print("設定が更新されました。")

    def _quit_app(self):
        """アプリケーションを終了"""
        print("なんでもショートカット を終了しています...")
        self.tray.stop()
        self.show_main_signal.close()
        self.root.after(0, self.root.destroy)


def main():
    """エントリーポイント"""
    show_main_on_start = "--background" not in sys.argv[1:]
    instance_guard = SingleInstanceGuard()
    if not instance_guard.acquire():
        MainWindowSignal().signal_existing_instance()
        print("なんでもショートカット は既に起動しています。")
        return

    try:
        app = NandemoShortcutApp(show_main_on_start=show_main_on_start)
        app.run()
    finally:
        instance_guard.release()


if __name__ == "__main__":
    main()
