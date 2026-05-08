"""
launcher.py - 常駐中アプリ表示用の軽量ランチャー
"""

from launch_protocol import MainWindowSignal, start_main_process


def main():
    signal = MainWindowSignal()
    if signal.signal_existing_instance():
        return

    start_main_process(background=False)


if __name__ == "__main__":
    main()
