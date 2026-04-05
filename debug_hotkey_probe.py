import keyboard


def dump(hotkey):
    print(f"[hotkey] {hotkey}")
    try:
        print("  parse_hotkey:", keyboard.parse_hotkey(hotkey))
    except Exception as exc:
        print("  parse_hotkey ERROR:", repr(exc))
    try:
        print("  parse_hotkey_combinations:", keyboard.parse_hotkey_combinations(hotkey))
    except Exception as exc:
        print("  parse_hotkey_combinations ERROR:", repr(exc))
    for token in hotkey.split("+"):
        token = token.strip()
        try:
            print(f"  key_to_scan_codes({token!r}):", keyboard.key_to_scan_codes(token))
        except Exception as exc:
            print(f"  key_to_scan_codes({token!r}) ERROR:", repr(exc))
    print()


if __name__ == "__main__":
    for item in ("pause", "ctrl+f1", "f1", "ctrl", "break"):
        dump(item)
