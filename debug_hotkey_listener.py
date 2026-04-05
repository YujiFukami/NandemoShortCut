"""
指定ホットキーの解釈と押下イベントを調べる簡易診断スクリプト。

使い方:
    python debug_hotkey_listener.py pause
    python debug_hotkey_listener.py ctrl+f1
"""

import sys
import threading

import keyboard


def main():
    hotkey = sys.argv[1] if len(sys.argv) > 1 else "pause"
    done = threading.Event()

    print(f"[target] {hotkey}")
    try:
        print("[parse_hotkey]", keyboard.parse_hotkey(hotkey))
    except Exception as exc:
        print("[parse_hotkey ERROR]", repr(exc))
    try:
        print("[parse_hotkey_combinations]", keyboard.parse_hotkey_combinations(hotkey))
    except Exception as exc:
        print("[parse_hotkey_combinations ERROR]", repr(exc))

    parts = [part.strip() for part in hotkey.split("+") if part.strip()]
    for part in parts:
        try:
            print(f"[scan_codes:{part}]", keyboard.key_to_scan_codes(part))
        except Exception as exc:
            print(f"[scan_codes:{part} ERROR]", repr(exc))

    def on_event(event):
        print(f"[event] type={event.event_type} name={event.name!r} scan_code={event.scan_code}")

    def on_trigger():
        print(f"[triggered] {hotkey}")
        done.set()

    print("キーイベントの監視を開始します。対象キーを押してください。Esc で終了します。")
    hook = keyboard.hook(on_event, suppress=False)
    hotkey_id = keyboard.add_hotkey(hotkey, on_trigger, suppress=False, trigger_on_release=False)
    esc_id = keyboard.add_hotkey("esc", done.set, suppress=False, trigger_on_release=False)
    try:
        done.wait()
    finally:
        keyboard.remove_hotkey(hotkey_id)
        keyboard.remove_hotkey(esc_id)
        keyboard.unhook(hook)


if __name__ == "__main__":
    main()
