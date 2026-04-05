"""
hotkey_listener.py - グローバルホットキー監視

keyboardライブラリを使用して、グローバルホットキーを監視する。
"""

import keyboard
class HotkeyListener:
    """グローバルホットキーを監視するクラス"""

    def __init__(self, activation_key="pause", on_activate=None):
        """
        Args:
            activation_key: 呼び出しキー名（例: "pause", "f1", "f12"）
            on_activate: 呼び出し時に実行するコールバック関数
        """
        self.activation_key = activation_key
        self.on_activate = on_activate
        self._hotkey_id = None
        self._running = False

    def start(self):
        """ホットキー監視を開始"""
        if self._running:
            return

        self._running = True
        self._register_hotkey()

    def stop(self):
        """ホットキー監視を停止"""
        self._running = False
        self._unregister_hotkey()

    def _register_hotkey(self):
        """ホットキーを登録"""
        try:
            self._unregister_hotkey()  # 既存の登録を解除
            self._hotkey_id = keyboard.add_hotkey(
                self.activation_key,
                self._on_hotkey_pressed,
                suppress=True,
                trigger_on_release=False,
            )
        except Exception as e:
            print(f"ホットキーの登録に失敗: {e}")
            self._hotkey_id = None

    def _unregister_hotkey(self):
        """ホットキーの登録を解除"""
        try:
            if self._hotkey_id is not None:
                keyboard.remove_hotkey(self._hotkey_id)
                self._hotkey_id = None
        except Exception:
            pass

    def _on_hotkey_pressed(self):
        """ホットキーが押された時のハンドラ"""
        if self.on_activate:
            self.on_activate()

    def update_activation_key(self, new_key):
        """呼び出しキーを変更"""
        was_running = self._running
        if was_running:
            self.stop()

        self.activation_key = new_key

        if was_running:
            self.start()
