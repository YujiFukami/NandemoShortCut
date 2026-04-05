"""
settings_window.py - 設定画面UI
"""

import tkinter as tk
from tkinter import ttk, messagebox, filedialog
from tkinter import font as tkfont

import keyboard

from action_executor import ActionExecutor
from startup_manager import is_startup_enabled, enable_startup, disable_startup


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
        self.activation_key_var = None
        self.startup_status_var = None

    def show(self):
        if self.window and self.window.winfo_exists():
            self._refresh_header_state()
            self.window.lift()
            self.window.focus_force()
            return

        self.window = tk.Toplevel(self.root)
        self.window.title("なんでもショートカット - 設定")
        self.window.geometry("760x560")
        self.window.configure(bg=self.BG_COLOR)
        self.window.minsize(680, 480)
        self._setup_styles()
        self._build_ui()
        self._refresh_list()
        self._refresh_header_state()
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

    def _refresh_header_state(self):
        if self.activation_key_var is not None:
            self.activation_key_var.set(self.config.activation_key)
        if self.startup_status_var is not None:
            self.startup_status_var.set("登録済み" if is_startup_enabled() else "未登録")

    def _notify_config_changed(self):
        self._refresh_header_state()
        if self.on_config_changed:
            self.on_config_changed()

    def _build_ui(self):
        main_font = tkfont.Font(family="Segoe UI", size=10)
        title_font = tkfont.Font(family="Segoe UI", size=14, weight="bold")
        btn_font = tkfont.Font(family="Segoe UI", size=10, weight="bold")

        header = tk.Frame(self.window, bg=self.BG_SECONDARY, pady=12)
        header.pack(fill=tk.X)
        tk.Label(header, text="🔑  なんでもショートカット", font=title_font, fg=self.TEXT_COLOR, bg=self.BG_SECONDARY).pack(side=tk.LEFT, padx=16)

        header_actions = tk.Frame(header, bg=self.BG_SECONDARY)
        header_actions.pack(side=tk.RIGHT, padx=16)

        hotkey_card = tk.Frame(header_actions, bg=self.BG_SECONDARY)
        hotkey_card.pack(side=tk.LEFT, padx=(0, 16))
        tk.Label(hotkey_card, text="呼び出しキー", font=main_font, fg="#a6adc8", bg=self.BG_SECONDARY).pack(anchor="e")
        hotkey_row = tk.Frame(hotkey_card, bg=self.BG_SECONDARY)
        hotkey_row.pack(anchor="e", pady=(4, 0))
        self.activation_key_var = tk.StringVar()
        tk.Label(hotkey_row, textvariable=self.activation_key_var, font=tkfont.Font(family="Consolas", size=11, weight="bold"), fg=self.ACCENT_COLOR, bg=self.BG_SECONDARY, width=20, anchor="e").pack(side=tk.LEFT, padx=(0, 8))
        self._make_button(hotkey_row, "キー入力で変更", self._open_hotkey_dialog, bg=self.ACCENT_COLOR, fg="#1e1e2e", font=btn_font).pack(side=tk.LEFT)

        startup_card = tk.Frame(header_actions, bg=self.BG_SECONDARY)
        startup_card.pack(side=tk.LEFT)
        tk.Label(startup_card, text="スタートアップ", font=main_font, fg="#a6adc8", bg=self.BG_SECONDARY).pack(anchor="e")
        startup_row = tk.Frame(startup_card, bg=self.BG_SECONDARY)
        startup_row.pack(anchor="e", pady=(4, 0))
        self.startup_status_var = tk.StringVar()
        tk.Label(startup_row, textvariable=self.startup_status_var, font=main_font, fg=self.TEXT_COLOR, bg=self.BG_SECONDARY, width=12, anchor="e").pack(side=tk.LEFT, padx=(0, 8))
        self._make_button(startup_row, "登録", self._enable_startup, bg=self.BTN_ADD, fg=self.BTN_ADD_FG, font=btn_font).pack(side=tk.LEFT, padx=(0, 8))
        self._make_button(startup_row, "解除", self._disable_startup, bg=self.BTN_BG, fg=self.TEXT_COLOR, font=btn_font).pack(side=tk.LEFT)

        content = tk.Frame(self.window, bg=self.BG_COLOR)
        content.pack(fill=tk.BOTH, expand=True, padx=16, pady=12)

        left_frame = tk.Frame(content, bg=self.BG_COLOR, width=180)
        left_frame.pack(side=tk.LEFT, fill=tk.Y, padx=(0, 8))
        left_frame.pack_propagate(False)
        tk.Label(left_frame, text="カテゴリ", font=main_font, fg=self.ACCENT_COLOR, bg=self.BG_COLOR, anchor="w").pack(fill=tk.X, pady=(0, 8))
        self.category_listbox = tk.Listbox(left_frame, bg=self.BG_INPUT, fg=self.TEXT_COLOR, selectbackground=self.ACCENT_COLOR, selectforeground="#1e1e2e", font=main_font, borderwidth=0, highlightthickness=1, highlightcolor=self.BORDER_COLOR, relief="flat")
        self.category_listbox.pack(fill=tk.BOTH, expand=True)
        self.category_listbox.bind("<<ListboxSelect>>", self._on_category_select)
        self._make_button(left_frame, "＋ カテゴリ追加", self._on_add_category, bg=self.ACCENT_COLOR, fg="#1e1e2e", font=tkfont.Font(family="Segoe UI", size=9, weight="bold")).pack(fill=tk.X, pady=(8, 0))

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
        self._make_button(btn_frame, "＋ 追加", self._on_add, bg=self.BTN_ADD, fg=self.BTN_ADD_FG, font=btn_font).pack(side=tk.LEFT, padx=(0, 8))
        self._make_button(btn_frame, "✏ 編集", self._on_edit, bg=self.BTN_BG, fg=self.TEXT_COLOR, font=btn_font).pack(side=tk.LEFT, padx=(0, 8))
        self._make_button(btn_frame, "🗑 削除", self._on_delete, bg=self.BTN_DEL, fg=self.BTN_DEL_FG, font=btn_font).pack(side=tk.LEFT)

        status_frame = tk.Frame(self.window, bg=self.BG_SECONDARY, pady=6)
        status_frame.pack(fill=tk.X)
        tk.Label(status_frame, text="呼び出しキーはボタンを押して実際のキー入力で登録できます。", font=main_font, fg="#a6adc8", bg=self.BG_SECONDARY).pack(side=tk.LEFT, padx=16)
        self.status_label = tk.Label(status_frame, text="● 常駐中", font=main_font, fg=self.BTN_ADD, bg=self.BG_SECONDARY)
        self.status_label.pack(side=tk.RIGHT, padx=16)

    def _refresh_list(self):
        self.category_listbox.delete(0, tk.END)
        self.category_listbox.insert(tk.END, "📋  すべて")
        for node in self.config.get_root_nodes():
            prefix = "📁" if node.is_group else "⚡"
            self.category_listbox.insert(tk.END, f"{prefix}  {node.label} ({node.key})")
        self.category_listbox.selection_set(0)
        self._refresh_tree()

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
        idx = selection[0]
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

    def _open_hotkey_dialog(self):
        HotkeyCaptureDialog(self.window, self.config.activation_key, self._apply_hotkey)

    def _apply_hotkey(self, hotkey):
        if hotkey == self.config.activation_key:
            return
        self.config.update_activation_key(hotkey)
        self._notify_config_changed()

    def _enable_startup(self):
        try:
            path = enable_startup()
        except OSError as e:
            messagebox.showerror("スタートアップ登録", str(e), parent=self.window)
            return
        self._refresh_header_state()
        messagebox.showinfo("スタートアップ登録", f"登録しました:\n{path}", parent=self.window)

    def _disable_startup(self):
        path = disable_startup()
        self._refresh_header_state()
        messagebox.showinfo("スタートアップ登録", f"解除しました:\n{path}", parent=self.window)

    def _on_add_category(self):
        CategoryDialog(self.window, self.config, on_save=self._on_action_saved)

    def _on_double_click(self, event):
        if self.tree.selection():
            self._on_edit()

    def _on_add(self):
        ActionDialog(self.window, self.config, on_save=self._on_action_saved)

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

    def _on_action_saved(self):
        self._refresh_list()
        self._notify_config_changed()


class ActionDialog:
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
        self.param_entries = {}
        self.dialog = tk.Toplevel(parent)
        self.dialog.title("アクション追加" if not edit_data else "アクション編集")
        self.dialog.geometry("420x400")
        self.dialog.configure(bg=self.BG_COLOR)
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
        group_options = ["（直接実行・新規グループ）"]
        self.group_keys = [None]
        for node in self.config.get_root_nodes():
            if node.is_group:
                group_options.append(f"{node.label} ({node.key})")
                self.group_keys.append(node.key)
        self.group_options = group_options
        self.group_var = tk.StringVar(value=group_options[0])
        group_combo = ttk.Combobox(main, textvariable=self.group_var, values=group_options, state="readonly", font=font)
        group_combo.pack(fill=tk.X, pady=(0, 12))
        if self.edit_data and self.edit_data.get("parent_key"):
            for i, gk in enumerate(self.group_keys):
                if gk == self.edit_data["parent_key"]:
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
        parent_key = self.group_keys[group_idx] if group_idx > 0 else None
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

    def __init__(self, parent, config_manager, on_save=None):
        self.config = config_manager
        self.on_save = on_save
        self.dialog = tk.Toplevel(parent)
        self.dialog.title("カテゴリ追加")
        self.dialog.geometry("360x220")
        self.dialog.configure(bg=self.BG_COLOR)
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
        tk.Label(main, text="カテゴリ名:", font=label_font, fg=self.TEXT_COLOR, bg=self.BG_COLOR).pack(anchor="w", pady=(0, 4))
        self.label_entry = tk.Entry(main, bg=self.BG_INPUT, fg=self.TEXT_COLOR, font=font, insertbackground=self.TEXT_COLOR, borderwidth=0, highlightthickness=1, highlightcolor=self.ACCENT_COLOR)
        self.label_entry.pack(fill=tk.X, pady=(0, 12), ipady=4)
        btn_frame = tk.Frame(main, bg=self.BG_COLOR, pady=8)
        btn_frame.pack(fill=tk.X)
        btn_font = tkfont.Font(family="Segoe UI", size=10, weight="bold")
        tk.Button(btn_frame, text="保存", command=self._on_save, bg=self.BTN_SAVE, fg="#1e1e2e", font=btn_font, relief="flat", padx=20, pady=4, cursor="hand2").pack(side=tk.RIGHT, padx=(8, 0))
        tk.Button(btn_frame, text="キャンセル", command=self.dialog.destroy, bg=self.BTN_CANCEL, fg=self.TEXT_COLOR, font=btn_font, relief="flat", padx=20, pady=4, cursor="hand2").pack(side=tk.RIGHT)

    def _on_save(self):
        try:
            self.config.add_group(self.key_entry.get().strip().upper(), self.label_entry.get().strip())
        except ValueError as e:
            messagebox.showwarning("入力エラー", str(e), parent=self.dialog)
            return
        self.dialog.destroy()
        if self.on_save:
            self.on_save()


class HotkeyCaptureDialog:
    BG_COLOR = "#1e1e2e"
    BG_SECONDARY = "#2d2d44"
    TEXT_COLOR = "#cdd6f4"
    ACCENT_COLOR = "#89b4fa"
    BTN_SAVE = "#a6e3a1"
    BTN_CANCEL = "#45475a"
    MODIFIERS = {"ctrl", "shift", "alt", "windows"}
    MODIFIER_LABELS = {"ctrl": "Ctrl", "shift": "Shift", "alt": "Alt", "windows": "Win"}

    def __init__(self, parent, initial_hotkey, on_save):
        self.on_save = on_save
        self.captured_hotkey = initial_hotkey
        self.modifiers = set()
        self.main_key = None
        self.dialog = tk.Toplevel(parent)
        self.dialog.title("呼び出しキー設定")
        self.dialog.geometry("440x250")
        self.dialog.configure(bg=self.BG_COLOR)
        self.dialog.transient(parent)
        self.dialog.grab_set()
        self.dialog.resizable(False, False)
        self.display_var = tk.StringVar(value=initial_hotkey)
        self.hint_var = tk.StringVar(value="入力欄を選択した状態で、設定したいキーの組み合わせを押してください")
        self._build_ui()
        self.capture_area.focus_force()
        self.dialog.update_idletasks()
        x = parent.winfo_x() + (parent.winfo_width() - 440) // 2
        y = parent.winfo_y() + (parent.winfo_height() - 250) // 2
        self.dialog.geometry(f"+{x}+{y}")

    def _build_ui(self):
        main = tk.Frame(self.dialog, bg=self.BG_COLOR, padx=24, pady=18)
        main.pack(fill=tk.BOTH, expand=True)
        tk.Label(main, text="呼び出しキーを記録", font=tkfont.Font(family="Segoe UI", size=14, weight="bold"), fg=self.TEXT_COLOR, bg=self.BG_COLOR).pack(anchor="w")
        tk.Label(main, textvariable=self.hint_var, font=tkfont.Font(family="Segoe UI", size=10), fg="#a6adc8", bg=self.BG_COLOR, wraplength=380, justify="left").pack(anchor="w", pady=(6, 12))
        self.capture_area = tk.Entry(main, textvariable=self.display_var, justify="center", bg=self.BG_SECONDARY, fg=self.ACCENT_COLOR, font=tkfont.Font(family="Consolas", size=16, weight="bold"), insertbackground=self.TEXT_COLOR, relief="flat", highlightthickness=2, highlightcolor=self.ACCENT_COLOR, highlightbackground=self.BG_SECONDARY)
        self.capture_area.pack(fill=tk.X, ipady=12)
        self.capture_area.bind("<KeyPress>", self._on_key_press)
        self.capture_area.bind("<KeyRelease>", self._on_key_release)
        helper = tk.Frame(main, bg=self.BG_COLOR)
        helper.pack(fill=tk.X, pady=(10, 0))
        tk.Label(helper, text="Esc でキャンセル / Backspace でクリア", font=tkfont.Font(family="Segoe UI", size=10), fg="#6c7086", bg=self.BG_COLOR).pack(side=tk.LEFT)
        tk.Button(helper, text="クリア", command=self._clear_capture, bg=self.BTN_CANCEL, fg=self.TEXT_COLOR, relief="flat", padx=14, cursor="hand2").pack(side=tk.RIGHT)
        btn_frame = tk.Frame(main, bg=self.BG_COLOR, pady=18)
        btn_frame.pack(fill=tk.X, side=tk.BOTTOM)
        btn_font = tkfont.Font(family="Segoe UI", size=10, weight="bold")
        tk.Button(btn_frame, text="保存", command=self._save, bg=self.BTN_SAVE, fg="#1e1e2e", font=btn_font, relief="flat", padx=20, pady=4, cursor="hand2").pack(side=tk.RIGHT, padx=(8, 0))
        tk.Button(btn_frame, text="キャンセル", command=self.dialog.destroy, bg=self.BTN_CANCEL, fg=self.TEXT_COLOR, font=btn_font, relief="flat", padx=20, pady=4, cursor="hand2").pack(side=tk.RIGHT)

    def _on_key_press(self, event):
        if event.keysym == "Escape":
            self.dialog.destroy()
            return "break"
        if event.keysym == "BackSpace":
            self._clear_capture()
            return "break"
        key_name = self._normalize_key(event.keysym)
        if not key_name:
            return "break"
        if key_name in self.MODIFIERS:
            self.modifiers.add(key_name)
            self.main_key = None
            self._update_display()
            return "break"
        self.main_key = key_name
        self._update_display()
        return "break"

    def _on_key_release(self, event):
        key_name = self._normalize_key(event.keysym)
        if key_name in self.MODIFIERS and self.main_key:
            self.modifiers.add(key_name)
        return "break"

    def _clear_capture(self):
        self.modifiers.clear()
        self.main_key = None
        self.captured_hotkey = ""
        self.display_var.set("")
        self.hint_var.set("入力欄を選択した状態で、設定したいキーの組み合わせを押してください")
        self.capture_area.focus_force()

    def _update_display(self):
        ordered = [name for name in ("ctrl", "shift", "alt", "windows") if name in self.modifiers]
        self.captured_hotkey = "+".join(ordered + ([self.main_key] if self.main_key else []))
        display = [self.MODIFIER_LABELS[name] for name in ordered]
        if self.main_key:
            display.append(self._format_main_key(self.main_key))
            self.hint_var.set("このキーの組み合わせで保存できます")
        else:
            self.hint_var.set("修飾キーだけでは保存できません。最後に通常キーを押してください")
        self.display_var.set(" + ".join(display))

    def _save(self):
        if not self.captured_hotkey:
            messagebox.showwarning("入力エラー", "呼び出しキーを入力してください", parent=self.dialog)
            return
        try:
            keyboard.parse_hotkey(self.captured_hotkey)
        except Exception:
            messagebox.showwarning("入力エラー", "このキーの組み合わせは使用できません", parent=self.dialog)
            return
        self.on_save(self.captured_hotkey)
        self.dialog.destroy()

    @staticmethod
    def _normalize_key(keysym):
        key = (keysym or "").lower()
        aliases = {"control_l": "ctrl", "control_r": "ctrl", "shift_l": "shift", "shift_r": "shift", "alt_l": "alt", "alt_r": "alt", "super_l": "windows", "super_r": "windows", "win_l": "windows", "win_r": "windows", "prior": "page up", "next": "page down", "return": "enter"}
        if key in aliases:
            return aliases[key]
        if key.startswith("f") and key[1:].isdigit():
            return key
        return key if key else None

    @staticmethod
    def _format_main_key(key_name):
        if len(key_name) == 1:
            return key_name.upper()
        return {"space": "Space", "enter": "Enter", "tab": "Tab", "page up": "PageUp", "page down": "PageDown", "pause": "Pause"}.get(key_name, key_name.title())
