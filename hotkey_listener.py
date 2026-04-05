"""
hotkey_listener.py - グローバルホットキー監視

keyboardライブラリを使用して、グローバルホットキーを監視する。
"""

import os

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
        self._debug_hook = None

    def start(self):
        """ホットキー監視を開始"""
        if self._running:
            return

        self._running = True
        self._start_debug_hook()
        self._register_hotkey()

    def stop(self):
        """ホットキー監視を停止"""
        self._running = False
        self._unregister_hotkey()
        self._stop_debug_hook()

    def _register_hotkey(self):
        """ホットキーを登録"""
        try:
            self._unregister_hotkey()  # 既存の登録を解除
            self._print_hotkey_diagnostics("registering")
            self._hotkey_id = keyboard.add_hotkey(
                self.activation_key,
                self._on_hotkey_pressed,
                suppress=True,
                trigger_on_release=False,
            )
            print(f"ホットキー登録成功: {self.activation_key} (id={self._hotkey_id})")
        except Exception as e:
            print(f"ホットキーの登録に失敗: {e}")
            self._hotkey_id = None

    def _unregister_hotkey(self):
        """ホットキーの登録を解除"""
        try:
            if self._hotkey_id is not None:
                keyboard.remove_hotkey(self._hotkey_id)
                print(f"ホットキー登録解除: {self.activation_key}")
                self._hotkey_id = None
        except Exception:
            pass

    def _on_hotkey_pressed(self):
        """ホットキーが押された時のハンドラ"""
        print(f"ホットキー検出: {self.activation_key}")
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

    def _start_debug_hook(self):
        """必要に応じて全キーイベントをログ出力"""
        if self._debug_hook is not None:
            return
        if os.environ.get("NANDEMO_SHORTCUT_DEBUG_HOTKEY") != "1":
            return
        print("ホットキーデバッグを有効化しました。キーイベントを出力します。")
        self._debug_hook = keyboard.hook(self._on_debug_event, suppress=False)

    def _stop_debug_hook(self):
        """デバッグ用キーイベントフックを解除"""
        if self._debug_hook is None:
            return
        try:
            keyboard.unhook(self._debug_hook)
        except Exception:
            pass
        self._debug_hook = None

    @staticmethod
    def _on_debug_event(event):
        print(
            "KEY_EVENT:",
            f"type={event.event_type}",
            f"name={event.name!r}",
            f"scan_code={event.scan_code}",
        )

    def _print_hotkey_diagnostics(self, phase):
        """ホットキーの解釈内容を出力"""
        print(f"ホットキー診断 ({phase}): {self.activation_key}")
        try:
            print(f"  parse_hotkey={keyboard.parse_hotkey(self.activation_key)}")
        except Exception as exc:
            print(f"  parse_hotkey failed: {exc}")
        try:
            print(f"  parse_hotkey_combinations={keyboard.parse_hotkey_combinations(self.activation_key)}")
        except Exception as exc:
            print(f"  parse_hotkey_combinations failed: {exc}")
