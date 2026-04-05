"""
action_executor.py - アクション実行エンジン

各アクションタイプに対応する実行ロジックを提供する。
"""

import os
import datetime
import webbrowser
import subprocess
import pyperclip

from explorer_utils import get_active_explorer_path, create_folder_in_path


class ActionExecutor:
    """アクションを実行するクラス"""

    def __init__(self):
        # アクションタイプ → 実行メソッドのマッピング
        self._handlers = {
            "create_folder": self._exec_create_folder,
            "clipboard_date": self._exec_clipboard_date,
            "clipboard_text": self._exec_clipboard_text,
            "open_url": self._exec_open_url,
            "open_path": self._exec_open_path,
            "run_command": self._exec_run_command,
            "type_text": self._exec_type_text,
        }

    def execute(self, action_node):
        """アクションノードを実行する。

        Args:
            action_node: ActionNode インスタンス

        Returns:
            tuple: (成功フラグ, メッセージ)
        """
        handler = self._handlers.get(action_node.action_type)
        if not handler:
            return False, f"未対応のアクションタイプ: {action_node.action_type}"

        try:
            return handler(action_node.params)
        except Exception as e:
            return False, f"アクション実行エラー: {e}"

    def _exec_create_folder(self, params):
        """フォルダ作成アクション"""
        folder_name = params.get("folderName", "")
        if not folder_name:
            return False, "フォルダ名が指定されていません"

        # アクティブなExplorerパスを取得
        explorer_path = get_active_explorer_path()
        if not explorer_path:
            return False, "Explorerウィンドウが見つかりません"

        return create_folder_in_path(explorer_path, folder_name)

    def _exec_clipboard_date(self, params):
        """日付をクリップボードにコピー"""
        fmt = params.get("format", "YYYYMMDD")
        now = datetime.datetime.now()

        # フォーマット変換
        date_str = fmt
        date_str = date_str.replace("YYYY", now.strftime("%Y"))
        date_str = date_str.replace("MM", now.strftime("%m"))
        date_str = date_str.replace("DD", now.strftime("%d"))
        date_str = date_str.replace("hh", now.strftime("%H"))
        date_str = date_str.replace("mm", now.strftime("%M"))
        date_str = date_str.replace("ss", now.strftime("%S"))

        pyperclip.copy(date_str)
        return True, f"日付をコピーしました: {date_str}"

    def _exec_clipboard_text(self, params):
        """テキストをクリップボードにコピー"""
        text = params.get("text", "")
        if not text:
            return False, "コピーするテキストが指定されていません"

        pyperclip.copy(text)
        return True, f"テキストをコピーしました: {text[:30]}..."

    def _exec_open_url(self, params):
        """URLをブラウザで開く"""
        url = params.get("url", "")
        if not url:
            return False, "URLが指定されていません"

        webbrowser.open(url)
        return True, f"URLを開きました: {url}"

    def _exec_open_path(self, params):
        """ファイルやフォルダを開く"""
        target_path = params.get("path", "")
        if not target_path:
            return False, "パスが指定されていません"

        target_path = os.path.expandvars(os.path.expanduser(target_path))
        if not os.path.exists(target_path):
            return False, f"パスが見つかりません: {target_path}"

        try:
            os.startfile(target_path)
            return True, f"開きました: {target_path}"
        except OSError as e:
            return False, f"起動に失敗: {e}"

    def _exec_run_command(self, params):
        """コマンドを実行"""
        command = params.get("command", "")
        if not command:
            return False, "コマンドが指定されていません"

        try:
            subprocess.Popen(command, shell=True)
            return True, f"コマンドを実行しました: {command}"
        except Exception as e:
            return False, f"コマンド実行エラー: {e}"

    def _exec_type_text(self, params):
        """キーストロークでテキスト入力"""
        text = params.get("text", "")
        if not text:
            return False, "入力するテキストが指定されていません"

        try:
            import keyboard
            # 少し待ってからタイプ（アプリが非表示になる時間を確保）
            import time
            time.sleep(0.3)
            keyboard.write(text, delay=0.02)
            return True, f"テキストを入力しました: {text[:30]}..."
        except Exception as e:
            return False, f"テキスト入力エラー: {e}"

    @staticmethod
    def get_action_types():
        """利用可能なアクションタイプとその表示名を返す"""
        return {
            "create_folder": "フォルダ作成",
            "clipboard_date": "日付コピー",
            "clipboard_text": "テキストコピー",
            "open_url": "URLを開く",
            "open_path": "ファイルを開く",
            "run_command": "コマンド実行",
            "type_text": "テキスト入力",
        }

    @staticmethod
    def get_param_fields(action_type):
        """アクションタイプに応じたパラメータフィールド定義を返す"""
        fields = {
            "create_folder": [
                {"name": "folderName", "label": "フォルダ名", "type": "text"},
            ],
            "clipboard_date": [
                {"name": "format", "label": "日付フォーマット", "type": "text", "default": "YYYYMMDD"},
            ],
            "clipboard_text": [
                {"name": "text", "label": "コピーするテキスト", "type": "text"},
            ],
            "open_url": [
                {"name": "url", "label": "URL", "type": "text"},
            ],
            "open_path": [
                {"name": "path", "label": "ファイルパス", "type": "file"},
            ],
            "run_command": [
                {"name": "command", "label": "コマンド", "type": "text"},
            ],
            "type_text": [
                {"name": "text", "label": "入力するテキスト", "type": "text"},
            ],
        }
        return fields.get(action_type, [])
