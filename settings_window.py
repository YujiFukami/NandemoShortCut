"""
settings_window.py - 設定画面UI
"""

import os
import tkinter as tk
from tkinter import ttk, messagebox, filedialog
from tkinter import font as tkfont
import webbrowser

from action_executor import ActionExecutor
from app_icon import apply_window_icon
from app_info import APP_VERSION, BLOG_URL, DEVELOPER_URL, GITHUB_URL


class SettingsWindow:
    BG_COLOR = "#1e1e2e"
    BG_SECONDARY = "#2d2d44"
    BG_INPUT = "#313244"
    TEXT_COLOR = "#cdd6f4"
    ACCENT_COLOR = "#89b4fa"
    BORDER_COLOR = "#45475a"
    BTN_BG = "#45475a"
    BTN_HOVER = "#585b70"
    BTN_ADD = "#a6e3a1"
    BTN_ADD_FG = "#1e1e2e"
    BTN_DEL = "#f38ba8"
    BTN_DEL_FG = "#1e1e2e"

    def __init__(self, root, config_manager, on_config_changed=None):
        self.root = root
        self.config = config_manager
        self.on_config_changed = on_config_changed
        self.window = None

    def show(self):
        if self.window and self.window.winfo_exists():
            self.window.lift()
            self.window.focus_force()
            return

        self.window = tk.Toplevel(self.root)
        self.window.title("なんでもショートカット - 設定")
        self.window.geometry("820x600")
        self.window.configure(bg=self.BG_COLOR)
        apply_window_icon(self.window)
        self.window.minsize(720, 520)
        self._setup_styles()
        self._build_ui()
        self._refresh_list()
        self.window.update_idletasks()
        w = self.window.winfo_width()
        h = self.window.winfo_height()
        x = (self.window.winfo_screenwidth() - w) // 2
        y = (self.window.winfo_screenheight() - h) // 2
        self.window.geometry(f"+{x}+{y}")

    def _setup_styles(self):
        style = ttk.Style()
        style.theme_use("clam")
        style.configure("Dark.Treeview", background=self.BG_COLOR, foreground=self.TEXT_COLOR, fieldbackground=self.BG_COLOR, borderwidth=0, font=("Segoe UI", 10))
        style.configure("Dark.Treeview.Heading", background=self.BG_SECONDARY, foreground=self.TEXT_COLOR, font=("Segoe UI", 10, "bold"))
        style.map("Dark.Treeview", background=[("selected", self.ACCENT_COLOR)], foreground=[("selected", "#1e1e2e")])

    def _make_button(self, parent, text, command, bg, fg, font):
        btn = tk.Button(parent, text=text, command=command, bg=bg, fg=fg, font=font, relief="flat", padx=16, pady=4, cursor="hand2", borderwidth=0)
        btn.bind("<Enter>", lambda e: btn.configure(bg=self.BTN_HOVER))
        btn.bind("<Leave>", lambda e: btn.configure(bg=bg))
        return btn

    def _notify_config_changed(self):
        if self.on_config_changed:
            self.on_config_changed()

    def _open_url(self, url):
        webbrowser.open(url)

    def _build_ui(self):
        main_font = tkfont.Font(family="Segoe UI", size=10)
        title_font = tkfont.Font(family="Segoe UI", size=14, weight="bold")
        btn_font = tkfont.Font(family="Segoe UI", size=10, weight="bold")

        header = tk.Frame(self.window, bg=self.BG_SECONDARY, pady=12)
        header.pack(fill=tk.X)
        tk.Label(header, text="🔑  なんでもショートカット", font=title_font, fg=self.TEXT_COLOR, bg=self.BG_SECONDARY).pack(side=tk.LEFT, padx=16)

        header_actions = tk.Frame(header, bg=self.BG_SECONDARY)
        header_actions.pack(side=tk.RIGHT, padx=16)

        tk.Label(
            header_actions,
            text="アクションとカテゴリを編集できます",
            font=main_font,
            fg="#a6adc8",
            bg=self.BG_SECONDARY,
        ).pack(anchor="e")
        link_row = tk.Frame(header_actions, bg=self.BG_SECONDARY)
        link_row.pack(anchor="e", pady=(6, 0))
        small_btn_font = tkfont.Font(family="Segoe UI", size=9, weight="bold")
        self._make_button(link_row, "使い方", lambda: self._open_url(BLOG_URL), bg=self.BTN_BG, fg=self.TEXT_COLOR, font=small_btn_font).pack(side=tk.LEFT, padx=(0, 6))
        self._make_button(link_row, "開発元", lambda: self._open_url(DEVELOPER_URL), bg=self.BTN_BG, fg=self.TEXT_COLOR, font=small_btn_font).pack(side=tk.LEFT, padx=(0, 6))
        self._make_button(link_row, "GitHub", lambda: self._open_url(GITHUB_URL), bg=self.BTN_BG, fg=self.TEXT_COLOR, font=small_btn_font).pack(side=tk.LEFT)

        content = tk.Frame(self.window, bg=self.BG_COLOR)
        content.pack(fill=tk.BOTH, expand=True, padx=16, pady=12)

        left_frame = tk.Frame(content, bg=self.BG_COLOR, width=180)
        left_frame.pack(side=tk.LEFT, fill=tk.Y, padx=(0, 8))
        left_frame.pack_propagate(False)
        tk.Label(left_frame, text="カテゴリ", font=main_font, fg=self.ACCENT_COLOR, bg=self.BG_COLOR, anchor="w").pack(fill=tk.X, pady=(0, 8))
        self.category_listbox = tk.Listbox(left_frame, bg=self.BG_INPUT, fg=self.TEXT_COLOR, selectbackground=self.ACCENT_COLOR, selectforeground="#1e1e2e", font=main_font, borderwidth=0, highlightthickness=1, highlightcolor=self.BORDER_COLOR, relief="flat")
        self.category_listbox.pack(fill=tk.BOTH, expand=True)
        self.category_listbox.bind("<<ListboxSelect>>", self._on_category_select)
        self.category_listbox.bind("<Double-1>", self._on_category_double_click)

        category_btn_frame = tk.Frame(left_frame, bg=self.BG_COLOR, pady=8)
        category_btn_frame.pack(fill=tk.X)
        category_btn_font = tkfont.Font(family="Segoe UI", size=9, weight="bold")
        self._make_button(category_btn_frame, "＋ 追加", self._on_add_category, bg=self.ACCENT_COLOR, fg="#1e1e2e", font=category_btn_font).pack(fill=tk.X, pady=(0, 6))
        self._make_button(category_btn_frame, "✏ 編集", self._on_edit_category, bg=self.BTN_BG, fg=self.TEXT_COLOR, font=category_btn_font).pack(fill=tk.X, pady=(0, 6))
        self._make_button(category_btn_frame, "🗑 カテゴリ削除", self._on_delete_category, bg=self.BTN_DEL, fg=self.BTN_DEL_FG, font=category_btn_font).pack(fill=tk.X)

        right_frame = tk.Frame(content, bg=self.BG_COLOR)
        right_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        tk.Label(right_frame, text="アクション一覧", font=main_font, fg=self.ACCENT_COLOR, bg=self.BG_COLOR, anchor="w").pack(fill=tk.X, pady=(0, 8))
        tree_frame = tk.Frame(right_frame, bg=self.BG_COLOR)
        tree_frame.pack(fill=tk.BOTH, expand=True)
        columns = ("key", "label", "type")
        self.tree = ttk.Treeview(tree_frame, columns=columns, show="headings", style="Dark.Treeview", selectmode="browse")
        self.tree.heading("key", text="キー")
        self.tree.heading("label", text="アクション名")
        self.tree.heading("type", text="タイプ")
        self.tree.column("key", width=80, minwidth=60)
        self.tree.column("label", width=240, minwidth=150)
        self.tree.column("type", width=140, minwidth=80)
        scrollbar = ttk.Scrollbar(tree_frame, orient=tk.VERTICAL, command=self.tree.yview)
        self.tree.configure(yscrollcommand=scrollbar.set)
        self.tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.tree.bind("<Double-1>", self._on_double_click)

        btn_frame = tk.Frame(right_frame, bg=self.BG_COLOR, pady=10)
        btn_frame.pack(fill=tk.X)

        action_btn_row = tk.Frame(btn_frame, bg=self.BG_COLOR)
        action_btn_row.pack(fill=tk.X)
        self._make_button(action_btn_row, "＋ アクション追加", self._on_add, bg=self.BTN_ADD, fg=self.BTN_ADD_FG, font=btn_font).pack(side=tk.LEFT, padx=(0, 8))
        self._make_button(action_btn_row, "✏ アクション編集", self._on_edit, bg=self.BTN_BG, fg=self.TEXT_COLOR, font=btn_font).pack(side=tk.LEFT, padx=(0, 8))
        self._make_button(action_btn_row, "🗑 アクション削除", self._on_delete, bg=self.BTN_DEL, fg=self.BTN_DEL_FG, font=btn_font).pack(side=tk.LEFT)

        config_btn_row = tk.Frame(btn_frame, bg=self.BG_COLOR)
        config_btn_row.pack(fill=tk.X, pady=(8, 0))
        self._make_button(config_btn_row, "読み込み", self._import_config, bg=self.BTN_BG, fg=self.TEXT_COLOR, font=btn_font).pack(side=tk.LEFT, padx=(0, 8))
        self._make_button(config_btn_row, "書き出し", self._export_config, bg=self.BTN_BG, fg=self.TEXT_COLOR, font=btn_font).pack(side=tk.LEFT, padx=(0, 8))
        self._make_button(config_btn_row, "設定フォルダ", self._open_config_folder, bg=self.BTN_BG, fg=self.TEXT_COLOR, font=btn_font).pack(side=tk.LEFT)

        status_frame = tk.Frame(self.window, bg=self.BG_SECONDARY, pady=6)
        status_frame.pack(fill=tk.X)
        tk.Label(status_frame, text="システムトレイのメニューからいつでもメイン画面を開けます。", font=main_font, fg="#a6adc8", bg=self.BG_SECONDARY).pack(side=tk.LEFT, padx=16)
        tk.Label(status_frame, text=f"v{APP_VERSION}", font=main_font, fg="#a6adc8", bg=self.BG_SECONDARY).pack(side=tk.RIGHT, padx=(0, 16))
        self.status_label = tk.Label(status_frame, text="● 常駐中", font=main_font, fg=self.BTN_ADD, bg=self.BG_SECONDARY)
        self.status_label.pack(side=tk.RIGHT, padx=(0, 10))

    def _refresh_list(self, selected_key=None):
        self.category_listbox.delete(0, tk.END)
        self.category_listbox.insert(tk.END, "📋  すべて")
        for node in self.config.get_root_nodes():
            prefix = "📁" if node.is_group else "⚡"
            self.category_listbox.insert(tk.END, f"{prefix}  {node.label} ({node.key})")
        selection_index = 0
        if selected_key:
            for index, node in enumerate(self.config.get_root_nodes(), start=1):
                if node.key == selected_key.upper():
                    selection_index = index
                    break
        self.category_listbox.selection_clear(0, tk.END)
        self.category_listbox.selection_set(selection_index)
        self.category_listbox.activate(selection_index)
        self._apply_category_selection(selection_index)

    def _refresh_tree(self, filter_key=None):
        self.tree.delete(*self.tree.get_children())
        type_names = ActionExecutor.get_action_types()
        for action in self.config.get_all_actions_flat():
            if filter_key and action.get("parent_key") != filter_key:
                continue
            self.tree.insert("", tk.END, values=(action["key_display"], action["label"], type_names.get(action["type"], action["type"])))

    def _on_category_select(self, event):
        selection = self.category_listbox.curselection()
        if not selection:
            return
        self._apply_category_selection(selection[0])

    def _apply_category_selection(self, idx):
        if idx == 0:
            self._refresh_tree()
            return
        nodes = self.config.get_root_nodes()
        if idx - 1 >= len(nodes):
            return
        node = nodes[idx - 1]
        if node.is_group:
            self._refresh_tree(filter_key=node.key)
            return
        self.tree.delete(*self.tree.get_children())
        type_names = ActionExecutor.get_action_types()
        self.tree.insert("", tk.END, values=(node.key, node.label, type_names.get(node.action_type, node.action_type)))

    def _on_add_category(self):
        CategoryDialog(self.window, self.config, on_save=self._on_action_saved)

    def _on_category_double_click(self, event):
        self._on_edit_category()

    def _get_selected_category_node(self):
        selection = self.category_listbox.curselection()
        if not selection:
            return None
        idx = selection[0]
        if idx == 0:
            return None
        nodes = self.config.get_root_nodes()
        if idx - 1 >= len(nodes):
            return None
        node = nodes[idx - 1]
        return node if node.is_group else None

    def _on_edit_category(self):
        node = self._get_selected_category_node()
        if not node:
            messagebox.showinfo("選択", "編集するカテゴリを選択してください", parent=self.window)
            return
        CategoryDialog(self.window, self.config, edit_data={"key": node.key, "label": node.label}, on_save=lambda: self._on_category_saved(node.key))

    def _on_delete_category(self):
        node = self._get_selected_category_node()
        if not node:
            messagebox.showinfo("選択", "削除するカテゴリを選択してください", parent=self.window)
            return
        message = f"カテゴリ「{node.label}」({node.key}) を削除しますか？"
        if node.children:
            message += "\n\nこのカテゴリ内のアクションも一緒に削除されます。"
        if not messagebox.askyesno("確認", message, parent=self.window):
            return
        try:
            self.config.remove_group(node.key)
        except ValueError as e:
            messagebox.showwarning("入力エラー", str(e), parent=self.window)
            return
        self._refresh_list()
        self._notify_config_changed()

    def _on_double_click(self, event):
        if self.tree.selection():
            self._on_edit()

    def _on_add(self):
        selected_category = self._get_selected_category_node()
        selected_key = selected_category.key if selected_category else None
        ActionDialog(
            self.window,
            self.config,
            initial_parent_key=selected_key,
            on_save=lambda: self._on_action_saved(selected_key),
        )

    def _find_selected_action(self):
        selected = self.tree.selection()
        if not selected:
            return None
        key_display = self.tree.item(selected[0])["values"][0]
        for action in self.config.get_all_actions_flat():
            if action["key_display"] == key_display:
                return action
        return None

    def _on_edit(self):
        target = self._find_selected_action()
        if not target:
            messagebox.showinfo("選択", "編集するアクションを選択してください", parent=self.window)
            return
        ActionDialog(self.window, self.config, edit_data=target, on_save=self._on_action_saved)

    def _on_delete(self):
        target = self._find_selected_action()
        if not target:
            messagebox.showinfo("選択", "削除するアクションを選択してください", parent=self.window)
            return
        if not messagebox.askyesno("確認", f"「{target['label']}」({target['key_display']}) を削除しますか？", parent=self.window):
            return
        self.config.remove_action(target["child_key"], target["parent_key"])
        self._refresh_list()
        self._notify_config_changed()

    def _import_config(self):
        path = filedialog.askopenfilename(
            parent=self.window,
            title="設定ファイルを読み込み",
            filetypes=[("JSON files", "*.json"), ("All files", "*.*")],
        )
        if not path:
            return
        if not messagebox.askyesno("設定読み込み", "現在の設定をバックアップして、選択した設定を読み込みますか？", parent=self.window):
            return
        try:
            backup_path = self.config.import_from_file(path, create_backup=True)
        except Exception as e:
            messagebox.showerror("設定読み込み", f"読み込みに失敗しました。\n{e}", parent=self.window)
            return
        self._refresh_list()
        self._notify_config_changed()
        message = "設定を読み込みました。"
        if backup_path:
            message += f"\n\nバックアップ:\n{backup_path}"
        messagebox.showinfo("設定読み込み", message, parent=self.window)

    def _export_config(self):
        path = filedialog.asksaveasfilename(
            parent=self.window,
            title="設定ファイルを書き出し",
            defaultextension=".json",
            initialfile="nandemo-shortcut-config.json",
            filetypes=[("JSON files", "*.json"), ("All files", "*.*")],
        )
        if not path:
            return
        try:
            self.config.export_to_file(path)
        except Exception as e:
            messagebox.showerror("設定書き出し", f"書き出しに失敗しました。\n{e}", parent=self.window)
            return
        messagebox.showinfo("設定書き出し", f"設定を書き出しました。\n{path}", parent=self.window)

    def _open_config_folder(self):
        try:
            os.startfile(self.config.get_config_dir())
        except OSError as e:
            messagebox.showerror("設定フォルダ", f"設定フォルダを開けませんでした。\n{e}", parent=self.window)

    def _on_action_saved(self, selected_key=None):
        self._refresh_list(selected_key=selected_key)
        self._notify_config_changed()

    def _on_category_saved(self, key=None):
        self._refresh_list(selected_key=key)
        self._notify_config_changed()


class ActionDialog:
    BG_COLOR = "#1e1e2e"
    BG_INPUT = "#313244"
    TEXT_COLOR = "#cdd6f4"
    ACCENT_COLOR = "#89b4fa"
    BTN_SAVE = "#a6e3a1"
    BTN_CANCEL = "#45475a"

    def __init__(self, parent, config_manager, edit_data=None, initial_parent_key=None, on_save=None):
        self.config = config_manager
        self.edit_data = edit_data
        self.initial_parent_key = initial_parent_key
        self.on_save = on_save
        self.param_entries = {}
        self.dialog = tk.Toplevel(parent)
        self.dialog.title("アクション追加" if not edit_data else "アクション編集")
        self.dialog.geometry("420x400")
        self.dialog.configure(bg=self.BG_COLOR)
        apply_window_icon(self.dialog)
        self.dialog.transient(parent)
        self.dialog.grab_set()
        self.dialog.resizable(False, False)
        self._build_ui()
        self.dialog.update_idletasks()
        x = parent.winfo_x() + (parent.winfo_width() - 420) // 2
        y = parent.winfo_y() + (parent.winfo_height() - 400) // 2
        self.dialog.geometry(f"+{x}+{y}")

    def _build_ui(self):
        font = tkfont.Font(family="Segoe UI", size=10)
        label_font = tkfont.Font(family="Segoe UI", size=10)
        main = tk.Frame(self.dialog, bg=self.BG_COLOR, padx=24, pady=16)
        main.pack(fill=tk.BOTH, expand=True)

        tk.Label(main, text="カテゴリ:", font=label_font, fg=self.TEXT_COLOR, bg=self.BG_COLOR).pack(anchor="w", pady=(0, 4))
        group_options = []
        self.group_keys = []
        for node in self.config.get_root_nodes():
            if node.is_group:
                group_options.append(f"{node.label} ({node.key})")
                self.group_keys.append(node.key)
        self.group_options = group_options
        self.group_var = tk.StringVar(value=group_options[0] if group_options else "")
        group_combo = ttk.Combobox(main, textvariable=self.group_var, values=group_options, state="readonly", font=font)
        group_combo.pack(fill=tk.X, pady=(0, 12))
        if not group_options:
            tk.Label(
                main,
                text="先にカテゴリを追加してください。アクションは必ずカテゴリ内に作成します。",
                font=label_font,
                fg="#f9e2af",
                bg=self.BG_COLOR,
                wraplength=360,
                justify=tk.LEFT,
            ).pack(anchor="w", pady=(0, 12))
        initial_group_key = None
        if self.edit_data and self.edit_data.get("parent_key"):
            initial_group_key = self.edit_data["parent_key"]
        elif self.initial_parent_key:
            initial_group_key = self.initial_parent_key
        if initial_group_key:
            for i, gk in enumerate(self.group_keys):
                if gk == initial_group_key:
                    group_combo.current(i)
                    break

        tk.Label(main, text="キー（1文字）:", font=label_font, fg=self.TEXT_COLOR, bg=self.BG_COLOR).pack(anchor="w", pady=(0, 4))
        self.key_entry = tk.Entry(main, bg=self.BG_INPUT, fg=self.TEXT_COLOR, font=tkfont.Font(family="Consolas", size=14, weight="bold"), insertbackground=self.TEXT_COLOR, borderwidth=0, highlightthickness=1, highlightcolor=self.ACCENT_COLOR)
        self.key_entry.pack(fill=tk.X, pady=(0, 12), ipady=4)
        if self.edit_data:
            self.key_entry.insert(0, self.edit_data.get("child_key", ""))

        tk.Label(main, text="アクション名:", font=label_font, fg=self.TEXT_COLOR, bg=self.BG_COLOR).pack(anchor="w", pady=(0, 4))
        self.label_entry = tk.Entry(main, bg=self.BG_INPUT, fg=self.TEXT_COLOR, font=font, insertbackground=self.TEXT_COLOR, borderwidth=0, highlightthickness=1, highlightcolor=self.ACCENT_COLOR)
        self.label_entry.pack(fill=tk.X, pady=(0, 12), ipady=4)
        if self.edit_data:
            self.label_entry.insert(0, self.edit_data.get("label", ""))

        tk.Label(main, text="タイプ:", font=label_font, fg=self.TEXT_COLOR, bg=self.BG_COLOR).pack(anchor="w", pady=(0, 4))
        type_names = ActionExecutor.get_action_types()
        self.type_keys = list(type_names.keys())
        type_display = list(type_names.values())
        self.type_var = tk.StringVar(value=type_display[0])
        type_combo = ttk.Combobox(main, textvariable=self.type_var, values=type_display, state="readonly", font=font)
        type_combo.pack(fill=tk.X, pady=(0, 12))
        type_combo.bind("<<ComboboxSelected>>", self._on_type_changed)
        if self.edit_data and self.edit_data.get("type") in type_names:
            type_combo.set(type_names[self.edit_data["type"]])

        self.param_frame = tk.Frame(main, bg=self.BG_COLOR)
        self.param_frame.pack(fill=tk.BOTH, expand=True)
        self._render_params()

        btn_frame = tk.Frame(main, bg=self.BG_COLOR, pady=8)
        btn_frame.pack(fill=tk.X)
        btn_font = tkfont.Font(family="Segoe UI", size=10, weight="bold")
        tk.Button(btn_frame, text="保存", command=self._on_save, bg=self.BTN_SAVE, fg="#1e1e2e", font=btn_font, relief="flat", padx=20, pady=4, cursor="hand2").pack(side=tk.RIGHT, padx=(8, 0))
        tk.Button(btn_frame, text="キャンセル", command=self.dialog.destroy, bg=self.BTN_CANCEL, fg=self.TEXT_COLOR, font=btn_font, relief="flat", padx=20, pady=4, cursor="hand2").pack(side=tk.RIGHT)

    def _get_selected_type_key(self):
        type_names = ActionExecutor.get_action_types()
        for key, display in type_names.items():
            if display == self.type_var.get():
                return key
        return self.type_keys[0] if self.type_keys else None

    def _on_type_changed(self, event=None):
        self._render_params()

    def _render_params(self):
        for widget in self.param_frame.winfo_children():
            widget.destroy()
        self.param_entries = {}
        fields = ActionExecutor.get_param_fields(self._get_selected_type_key())
        font = tkfont.Font(family="Segoe UI", size=10)
        for field in fields:
            tk.Label(self.param_frame, text=f"{field['label']}:", font=font, fg=self.TEXT_COLOR, bg=self.BG_COLOR).pack(anchor="w", pady=(0, 4))
            row = tk.Frame(self.param_frame, bg=self.BG_COLOR)
            row.pack(fill=tk.X, pady=(0, 8))
            entry = tk.Entry(row, bg=self.BG_INPUT, fg=self.TEXT_COLOR, font=font, insertbackground=self.TEXT_COLOR, borderwidth=0, highlightthickness=1, highlightcolor=self.ACCENT_COLOR)
            entry.pack(side=tk.LEFT, fill=tk.X, expand=True, ipady=4)
            default = field.get("default", "")
            if self.edit_data and field["name"] in self.edit_data.get("params", {}):
                default = self.edit_data["params"][field["name"]]
            if default:
                entry.insert(0, default)
            self.param_entries[field["name"]] = entry
            if field.get("type") == "file":
                tk.Button(row, text="参照", command=lambda name=field["name"]: self._browse_file(name), bg=self.BTN_CANCEL, fg=self.TEXT_COLOR, font=font, relief="flat", padx=12, cursor="hand2").pack(side=tk.LEFT, padx=(8, 0))

    def _browse_file(self, field_name):
        selected = filedialog.askopenfilename(parent=self.dialog, title="ファイルを選択")
        if selected:
            entry = self.param_entries.get(field_name)
            entry.delete(0, tk.END)
            entry.insert(0, selected)

    def _on_save(self):
        key = self.key_entry.get().strip().upper()
        label = self.label_entry.get().strip()
        action_type = self._get_selected_type_key()
        params = {name: entry.get().strip() for name, entry in self.param_entries.items() if entry.get().strip()}
        try:
            group_idx = self.group_options.index(self.group_var.get())
        except ValueError:
            group_idx = 0
        parent_key = self.group_keys[group_idx] if 0 <= group_idx < len(self.group_keys) else None
        if not parent_key:
            messagebox.showwarning("入力エラー", "カテゴリを選択してください。アクションは必ずカテゴリ内に作成します。", parent=self.dialog)
            return
        try:
            if self.edit_data:
                self.config.update_action(self.edit_data["child_key"], self.edit_data.get("parent_key"), key, label, action_type, params, parent_key)
            else:
                self.config.add_action(key, label, action_type, params, parent_key)
        except ValueError as e:
            messagebox.showwarning("入力エラー", str(e), parent=self.dialog)
            return
        self.dialog.destroy()
        if self.on_save:
            self.on_save()


class CategoryDialog:
    BG_COLOR = "#1e1e2e"
    BG_INPUT = "#313244"
    TEXT_COLOR = "#cdd6f4"
    ACCENT_COLOR = "#89b4fa"
    BTN_SAVE = "#a6e3a1"
    BTN_CANCEL = "#45475a"

    def __init__(self, parent, config_manager, edit_data=None, on_save=None):
        self.config = config_manager
        self.edit_data = edit_data
        self.on_save = on_save
        self.dialog = tk.Toplevel(parent)
        self.dialog.title("カテゴリ追加" if not edit_data else "カテゴリ編集")
        self.dialog.geometry("360x220")
        self.dialog.configure(bg=self.BG_COLOR)
        apply_window_icon(self.dialog)
        self.dialog.transient(parent)
        self.dialog.grab_set()
        self.dialog.resizable(False, False)
        self._build_ui()
        self.dialog.update_idletasks()
        x = parent.winfo_x() + (parent.winfo_width() - 360) // 2
        y = parent.winfo_y() + (parent.winfo_height() - 220) // 2
        self.dialog.geometry(f"+{x}+{y}")

    def _build_ui(self):
        font = tkfont.Font(family="Segoe UI", size=10)
        label_font = tkfont.Font(family="Segoe UI", size=10)
        main = tk.Frame(self.dialog, bg=self.BG_COLOR, padx=24, pady=16)
        main.pack(fill=tk.BOTH, expand=True)
        tk.Label(main, text="キー（1文字）:", font=label_font, fg=self.TEXT_COLOR, bg=self.BG_COLOR).pack(anchor="w", pady=(0, 4))
        self.key_entry = tk.Entry(main, bg=self.BG_INPUT, fg=self.TEXT_COLOR, font=tkfont.Font(family="Consolas", size=14, weight="bold"), insertbackground=self.TEXT_COLOR, borderwidth=0, highlightthickness=1, highlightcolor=self.ACCENT_COLOR)
        self.key_entry.pack(fill=tk.X, pady=(0, 12), ipady=4)
        if self.edit_data:
            self.key_entry.insert(0, self.edit_data.get("key", ""))
        tk.Label(main, text="カテゴリ名:", font=label_font, fg=self.TEXT_COLOR, bg=self.BG_COLOR).pack(anchor="w", pady=(0, 4))
        self.label_entry = tk.Entry(main, bg=self.BG_INPUT, fg=self.TEXT_COLOR, font=font, insertbackground=self.TEXT_COLOR, borderwidth=0, highlightthickness=1, highlightcolor=self.ACCENT_COLOR)
        self.label_entry.pack(fill=tk.X, pady=(0, 12), ipady=4)
        if self.edit_data:
            self.label_entry.insert(0, self.edit_data.get("label", ""))
        btn_frame = tk.Frame(main, bg=self.BG_COLOR, pady=8)
        btn_frame.pack(fill=tk.X)
        btn_font = tkfont.Font(family="Segoe UI", size=10, weight="bold")
        tk.Button(btn_frame, text="保存", command=self._on_save, bg=self.BTN_SAVE, fg="#1e1e2e", font=btn_font, relief="flat", padx=20, pady=4, cursor="hand2").pack(side=tk.RIGHT, padx=(8, 0))
        tk.Button(btn_frame, text="キャンセル", command=self.dialog.destroy, bg=self.BTN_CANCEL, fg=self.TEXT_COLOR, font=btn_font, relief="flat", padx=20, pady=4, cursor="hand2").pack(side=tk.RIGHT)

    def _on_save(self):
        try:
            key = self.key_entry.get().strip().upper()
            label = self.label_entry.get().strip()
            if self.edit_data:
                self.config.update_group(self.edit_data["key"], key, label)
            else:
                self.config.add_group(key, label)
        except ValueError as e:
            messagebox.showwarning("入力エラー", str(e), parent=self.dialog)
            return
        self.dialog.destroy()
        if self.on_save:
            self.on_save()
