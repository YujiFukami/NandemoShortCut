"""
tray_icon.py - システムトレイアイコン

pystrayを使用してシステムトレイに常駐し、
右クリックメニューを提供する。
"""

import threading
from PIL import Image, ImageDraw, ImageFont
import pystray
from pystray import MenuItem, Menu


class TrayIcon:
    """システムトレイアイコン"""

    def __init__(self, on_open_main=None, on_settings=None, on_quit=None):
        """
        Args:
            on_open_main: メイン画面を開くコールバック
            on_settings: 設定画面を開くコールバック
            on_quit: 終了時のコールバック
        """
        self.on_open_main = on_open_main
        self.on_settings = on_settings
        self.on_quit = on_quit
        self.icon = None
        self._thread = None

    def start(self):
        """トレイアイコンを表示"""
        icon_image = self._create_icon_image()

        menu = Menu(
            MenuItem("メイン画面を開く", self._on_open_main_click, default=True),
            MenuItem("設定を開く", self._on_settings_click),
            Menu.SEPARATOR,
            MenuItem("終了", self._on_quit_click),
        )

        self.icon = pystray.Icon(
            name="nandemo_shortcut",
            icon=icon_image,
            title="なんでもショートカット",
            menu=menu,
        )

        # 別スレッドで実行
        self._thread = threading.Thread(target=self.icon.run, daemon=True)
        self._thread.start()

    def stop(self):
        """トレイアイコンを削除"""
        if self.icon:
            try:
                self.icon.stop()
            except Exception:
                pass

    def _create_icon_image(self):
        """トレイアイコン画像を生成"""
        size = 64
        image = Image.new("RGBA", (size, size), (0, 0, 0, 0))
        draw = ImageDraw.Draw(image)

        # 背景（丸角風の四角）
        draw.rounded_rectangle(
            [4, 4, size - 4, size - 4],
            radius=12,
            fill="#89b4fa"
        )

        # 鍵アイコンを簡易的に描画
        # キーの頭部分（円）
        draw.ellipse([18, 12, 46, 36], fill="#1e1e2e")
        draw.ellipse([24, 16, 40, 30], fill="#89b4fa")

        # キーの柄部分
        draw.rectangle([28, 30, 36, 52], fill="#1e1e2e")
        draw.rectangle([36, 38, 44, 42], fill="#1e1e2e")
        draw.rectangle([36, 46, 42, 50], fill="#1e1e2e")

        return image

    def _on_settings_click(self, icon=None, item=None):
        """設定メニュークリック"""
        if self.on_settings:
            self.on_settings()

    def _on_open_main_click(self, icon=None, item=None):
        """メイン画面を開く"""
        if self.on_open_main:
            self.on_open_main()

    def _on_quit_click(self, icon=None, item=None):
        """終了メニュークリック"""
        if self.on_quit:
            self.on_quit()
