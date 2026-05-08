"""
overlay_window.py - 呼び出し時オーバーレイ表示

呼び出しキー押下時に表示されるオーバーレイウィンドウ。
登録済みアクションをキーガイドとして表示し、キー入力を受け付ける。
"""

import tkinter as tk
from tkinter import font as tkfont

from app_info import APP_VERSION


class OverlayWindow:
    """呼び出し時のオーバーレイウィンドウ"""

    # ダークテーマカラー
    BG_COLOR = "#1e1e2e"
    BG_HEADER = "#2d2d44"
    TEXT_COLOR = "#cdd6f4"
    KEY_COLOR = "#f5c2e7"
    ARROW_COLOR = "#89b4fa"
    BORDER_COLOR = "#45475a"
    HIGHLIGHT_BG = "#313244"
    SUCCESS_COLOR = "#a6e3a1"
    ERROR_COLOR = "#f38ba8"

    def __init__(self, root, config_manager, action_executor, on_complete=None, on_open_settings=None):
        """
        Args:
            root: tkinter root ウィンドウ
            config_manager: ConfigManager インスタンス
            action_executor: ActionExecutor インスタンス
            on_complete: アクション完了/キャンセル時のコールバック
            on_open_settings: 設定画面を開くコールバック
        """
        self.root = root
        self.config = config_manager
        self.executor = action_executor
        self.on_complete = on_complete
        self.on_open_settings = on_open_settings

        self.window = None
        self.current_group = None  # 現在のグループノード（None=ルート）
        self._visible = False

    def show(self):
        """オーバーレイを表示"""
        self.current_group = None
        self._create_window()
        self._render_items()
        self._visible = True

    def hide(self):
        """オーバーレイを非表示"""
        self._visible = False
        if self.window:
            try:
                self.window.destroy()
            except Exception:
                pass
            self.window = None

    def is_visible(self):
        """表示中かどうか"""
        return self._visible

    def _create_window(self):
        """オーバーレイウィンドウを作成"""
        if self.window:
            try:
                self.window.destroy()
            except Exception:
                pass

        self.window = tk.Toplevel(self.root)
        self.window.title("なんでもショートカット")
        self.window.overrideredirect(True)  # タイトルバーなし
        self.window.attributes("-topmost", True)
        self.window.attributes("-alpha", 0.95)
        self.window.configure(bg=self.BG_COLOR)

        # 画面中央に配置
        self.window.update_idletasks()
        self._center_window(360, 400)

        # キーイベントをバインド
        self.window.bind("<Key>", self._on_key)
        self.window.bind("<Escape>", self._on_escape)
        self.window.focus_force()

    def _center_window(self, width, height):
        """ウィンドウを画面中央に配置"""
        screen_w = self.window.winfo_screenwidth()
        screen_h = self.window.winfo_screenheight()
        x = (screen_w - width) // 2
        y = (screen_h - height) // 2
        self.window.geometry(f"{width}x{height}+{x}+{y}")

    def _render_items(self):
        """現在のレベルのアクション一覧を描画"""
        if not self.window:
            return

        # 既存ウィジェットをクリア
        for widget in self.window.winfo_children():
            widget.destroy()

        # メインフレーム
        main_frame = tk.Frame(self.window, bg=self.BG_COLOR)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=2, pady=2)

        # ヘッダー
        header_frame = tk.Frame(main_frame, bg=self.BG_HEADER, pady=12)
        header_frame.pack(fill=tk.X)

        title_font = tkfont.Font(family="Segoe UI", size=13, weight="bold")
        sub_font = tkfont.Font(family="Segoe UI", size=10)

        if self.current_group:
            title_text = f"🔑  {self.current_group.label}"
            sub_text = f"{self.current_group.key} →  次のキーを押してください"
        else:
            title_text = "🔑  なんでもショートカット"
            sub_text = "キーを押してください"

        tk.Label(
            header_frame, text=title_text, font=title_font,
            fg=self.TEXT_COLOR, bg=self.BG_HEADER, anchor="w"
        ).pack(fill=tk.X, padx=16)

        tk.Label(
            header_frame, text=sub_text, font=sub_font,
            fg=self.ARROW_COLOR, bg=self.BG_HEADER, anchor="w"
        ).pack(fill=tk.X, padx=16)

        # セパレータ
        tk.Frame(main_frame, bg=self.BORDER_COLOR, height=1).pack(fill=tk.X)

        # アクション一覧
        list_frame = tk.Frame(main_frame, bg=self.BG_COLOR)
        list_frame.pack(fill=tk.BOTH, expand=True, pady=8)

        item_font = tkfont.Font(family="Segoe UI", size=12)
        key_font = tkfont.Font(family="Consolas", size=14, weight="bold")

        # 表示するノードを決定
        if self.current_group:
            nodes = list(self.current_group.children.values())
        else:
            nodes = self.config.get_root_nodes()

        for node in nodes:
            row = tk.Frame(list_frame, bg=self.BG_COLOR, pady=4)
            row.pack(fill=tk.X, padx=12)

            # ホバーエフェクト
            row.bind("<Enter>", lambda e, r=row: r.configure(bg=self.HIGHLIGHT_BG))
            row.bind("<Leave>", lambda e, r=row: r.configure(bg=self.BG_COLOR))

            # キー表示
            key_label = tk.Label(
                row, text=f"  {node.key}  ", font=key_font,
                fg=self.KEY_COLOR, bg=self.BG_COLOR,
                padx=8, pady=4
            )
            key_label.pack(side=tk.LEFT)

            # アクション名
            label_text = node.label
            if node.is_group:
                label_text += "  →"

            name_label = tk.Label(
                row, text=label_text, font=item_font,
                fg=self.TEXT_COLOR, bg=self.BG_COLOR,
                anchor="w", padx=8
            )
            name_label.pack(side=tk.LEFT, fill=tk.X, expand=True)

        # セパレータ
        tk.Frame(main_frame, bg=self.BORDER_COLOR, height=1).pack(fill=tk.X, pady=(8, 0))

        # フッター
        footer_frame = tk.Frame(main_frame, bg=self.BG_COLOR, pady=8)
        footer_frame.pack(fill=tk.X)

        esc_text = "ESC  戻る" if self.current_group else "ESC  キャンセル"
        footer_top = tk.Frame(footer_frame, bg=self.BG_COLOR)
        footer_top.pack(fill=tk.X, padx=16)
        tk.Label(
            footer_top, text=esc_text, font=sub_font,
            fg="#6c7086", bg=self.BG_COLOR
        ).pack(side=tk.LEFT)
        tk.Label(
            footer_top, text=f"v{APP_VERSION}", font=sub_font,
            fg="#6c7086", bg=self.BG_COLOR
        ).pack(side=tk.RIGHT)

        if not self.current_group:
            action_row = tk.Frame(footer_frame, bg=self.BG_COLOR)
            action_row.pack(fill=tk.X, padx=16, pady=(8, 0))

            tk.Label(
                action_row, text="S  設定を開く", font=sub_font,
                fg=self.ARROW_COLOR, bg=self.BG_COLOR
            ).pack(side=tk.LEFT)

            tk.Button(
                action_row,
                text="設定",
                command=self._open_settings,
                bg=self.BG_HEADER,
                fg=self.TEXT_COLOR,
                relief="flat",
                padx=12,
                pady=3,
                cursor="hand2",
            ).pack(side=tk.RIGHT)

        # ウィンドウサイズを内容に合わせて調整
        self.window.update_idletasks()
        req_height = main_frame.winfo_reqheight() + 4
        req_height = max(req_height, 200)
        self._center_window(360, req_height)

        # フォーカスを確保
        self.window.focus_force()

    def _on_key(self, event):
        """キー入力のハンドラ"""
        key = event.char.upper() if event.char else event.keysym.upper()

        if not key or key == "ESCAPE":
            return

        if not self.current_group and key == "S":
            self._open_settings()
            return

        # 現在のレベルでノードを探す
        if self.current_group:
            node = self.current_group.get_child(key)
        else:
            node = self.config.get_node_by_key(key)

        if not node:
            # 登録されていないキー → 無視
            return

        if node.is_group:
            # グループの場合 → 次の階層に進む
            self.current_group = node
            self._render_items()
        else:
            # アクションの場合 → 実行
            self._execute_action(node)

    def _open_settings(self):
        """設定画面を開く"""
        self.hide()
        if self.on_open_settings:
            self.on_open_settings()

    def _on_escape(self, event):
        """ESCキーのハンドラ"""
        if self.current_group:
            # グループ内 → ルートに戻る
            self.current_group = None
            self._render_items()
        else:
            # ルート → 閉じる
            self.hide()
            if self.on_complete:
                self.on_complete(False, "キャンセルしました")

    def _execute_action(self, node):
        """アクションを実行して結果を表示"""
        self.hide()
        success, message = self.executor.execute(node)

        if self.on_complete:
            self.on_complete(success, message)

        # 結果を短時間だけ表示
        self._show_result(success, message)

    def _show_result(self, success, message):
        """実行結果を一時的に表示"""
        result_win = tk.Toplevel(self.root)
        result_win.overrideredirect(True)
        result_win.attributes("-topmost", True)
        result_win.attributes("-alpha", 0.9)

        color = self.SUCCESS_COLOR if success else self.ERROR_COLOR
        icon = "✓" if success else "✗"

        result_win.configure(bg=self.BG_COLOR)

        frame = tk.Frame(result_win, bg=self.BG_COLOR, padx=20, pady=12)
        frame.pack()

        result_font = tkfont.Font(family="Segoe UI", size=11)
        tk.Label(
            frame, text=f"{icon}  {message}", font=result_font,
            fg=color, bg=self.BG_COLOR
        ).pack()

        # 画面中央に配置
        result_win.update_idletasks()
        w = result_win.winfo_reqwidth()
        h = result_win.winfo_reqheight()
        screen_w = result_win.winfo_screenwidth()
        screen_h = result_win.winfo_screenheight()
        x = (screen_w - w) // 2
        y = (screen_h - h) // 2
        result_win.geometry(f"+{x}+{y}")

        # 1.5秒後に自動で閉じる
        result_win.after(1500, result_win.destroy)
