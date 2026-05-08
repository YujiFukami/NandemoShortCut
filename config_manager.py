"""
config_manager.py - 設定ファイルの管理

JSON設定ファイルの読み込み・保存・バリデーション。
キーツリー（Trie）構造の構築・検索。
"""

import json
import os
import shutil
import sys
from datetime import datetime


def _get_config_dir():
    """設定ファイルを保存するディレクトリを取得する。
    EXE実行時はEXEと同じフォルダ、開発時はスクリプトと同じフォルダ。"""
    if getattr(sys, 'frozen', False):
        # PyInstallerでEXE化された場合
        return os.path.dirname(sys.executable)
    else:
        # 開発時（python main.py）
        return os.path.dirname(os.path.abspath(__file__))


# デフォルト設定ファイルのパス
DEFAULT_CONFIG_PATH = os.path.join(_get_config_dir(), "config.json")


class ActionNode:
    """キーツリーの各ノードを表すクラス"""

    def __init__(self, key="", label="", action_type=None, params=None, is_group=False):
        self.key = key.upper()
        self.label = label
        self.action_type = action_type  # None の場合はグループノード
        self.params = params or {}
        self.is_group = is_group
        self.children = {}  # key(大文字) -> ActionNode

    def add_child(self, node):
        """子ノードを追加"""
        self.children[node.key] = node

    def get_child(self, key):
        """キーに対応する子ノードを取得"""
        return self.children.get(key.upper())

    def has_children(self):
        """子ノードを持つか"""
        return len(self.children) > 0

    def to_dict(self):
        """辞書形式に変換（JSON保存用）"""
        d = {
            "key": self.key,
            "label": self.label,
        }
        if self.is_group:
            d["isGroup"] = True
            d["children"] = [child.to_dict() for child in self.children.values()]
        else:
            d["type"] = self.action_type
            d["params"] = self.params
        return d

    def __repr__(self):
        if self.is_group:
            return f"ActionNode(key={self.key}, label={self.label}, group, children={len(self.children)})"
        return f"ActionNode(key={self.key}, label={self.label}, type={self.action_type})"


class ConfigManager:
    """設定ファイルを管理するクラス"""

    def __init__(self, config_path=None):
        self.config_path = config_path or DEFAULT_CONFIG_PATH
        self.root_actions = {}  # key(大文字) -> ActionNode
        self._raw_config = {}
        self.load()

    def load(self):
        """設定ファイルを読み込み"""
        if not os.path.exists(self.config_path):
            self._create_default_config()
            return

        try:
            with open(self.config_path, "r", encoding="utf-8") as f:
                self._raw_config = json.load(f)
        except (json.JSONDecodeError, IOError) as e:
            print(f"設定ファイルの読み込みに失敗: {e}")
            self._create_default_config()
            return

        self._build_tree(self._raw_config.get("actions", []))

    def _build_tree(self, actions_list):
        """アクションリストからキーツリーを構築"""
        self.root_actions = {}
        for action_data in actions_list:
            node = self._parse_action(action_data)
            if node:
                self.root_actions[node.key] = node

    def _parse_action(self, data):
        """辞書データからActionNodeを構築"""
        key = data.get("key", "").upper()
        label = data.get("label", "")
        is_group = data.get("isGroup", False)

        if is_group:
            node = ActionNode(key=key, label=label, is_group=True)
            for child_data in data.get("children", []):
                child = self._parse_action(child_data)
                if child:
                    node.add_child(child)
            return node
        else:
            return ActionNode(
                key=key,
                label=label,
                action_type=data.get("type"),
                params=data.get("params", {}),
            )

    def save(self):
        """設定をJSONファイルに保存"""
        config = {
            "actions": [node.to_dict() for node in self.root_actions.values()],
        }
        try:
            with open(self.config_path, "w", encoding="utf-8") as f:
                json.dump(config, f, ensure_ascii=False, indent=2)
        except IOError as e:
            print(f"設定ファイルの保存に失敗: {e}")

    def get_config_dir(self):
        """設定ファイルがあるフォルダを返す"""
        return os.path.dirname(os.path.abspath(self.config_path))

    def export_to_file(self, export_path):
        """現在の設定ファイルを指定先へ書き出す"""
        self.save()
        shutil.copy2(self.config_path, export_path)

    def import_from_file(self, import_path, create_backup=True):
        """外部JSONを検証して現在の設定ファイルへ読み込む"""
        with open(import_path, "r", encoding="utf-8") as f:
            data = json.load(f)
        if not isinstance(data.get("actions"), list):
            raise ValueError("actions が見つからないか、形式が正しくありません")

        backup_path = None
        if create_backup and os.path.exists(self.config_path):
            backup_path = self._create_backup()

        if os.path.abspath(import_path) != os.path.abspath(self.config_path):
            shutil.copy2(import_path, self.config_path)
        self.load()
        return backup_path

    def _create_backup(self):
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        base_name = f"config.backup.{timestamp}.json"
        backup_path = os.path.join(self.get_config_dir(), base_name)
        shutil.copy2(self.config_path, backup_path)
        return backup_path

    def _create_default_config(self):
        """デフォルト設定を生成"""
        self.root_actions = {}

    def get_root_nodes(self):
        """ルートレベルのアクションノードを返す"""
        return list(self.root_actions.values())

    def get_node_by_key(self, key):
        """キーに対応するルートノードを取得"""
        return self.root_actions.get(key.upper())

    def add_action(self, key, label, action_type, params, parent_key=None):
        """アクションを追加"""
        self._validate_single_key(key)
        self._validate_label(label)
        container = self._get_action_container(parent_key)
        normalized_key = key.upper()
        if normalized_key in container:
            raise ValueError(f"キー '{normalized_key}' は既に使用されています")

        new_node = ActionNode(key=key, label=label, action_type=action_type, params=params)
        container[normalized_key] = new_node

        self.save()

    def add_group(self, key, label):
        """グループを追加"""
        self._validate_single_key(key)
        self._validate_label(label)
        normalized_key = key.upper()
        if normalized_key in self.root_actions:
            raise ValueError(f"キー '{normalized_key}' は既に使用されています")

        group = ActionNode(key=key, label=label, is_group=True)
        self.root_actions[normalized_key] = group
        self.save()

    def update_group(self, old_key, new_key, label):
        """既存カテゴリを更新"""
        self._validate_single_key(new_key)
        self._validate_label(label)

        old_normalized_key = old_key.upper()
        node = self.root_actions.get(old_normalized_key)
        if not node or not node.is_group:
            raise ValueError("編集対象のカテゴリが見つかりません")

        new_normalized_key = new_key.upper()
        if old_normalized_key != new_normalized_key and new_normalized_key in self.root_actions:
            raise ValueError(f"キー '{new_normalized_key}' は既に使用されています")

        del self.root_actions[old_normalized_key]
        node.key = new_normalized_key
        node.label = label
        self.root_actions[new_normalized_key] = node
        self.save()

    def remove_group(self, key):
        """カテゴリを削除"""
        normalized_key = (key or "").strip().upper()
        node = self.root_actions.get(normalized_key)
        if not node or not node.is_group:
            raise ValueError("削除対象のカテゴリが見つかりません")

        del self.root_actions[normalized_key]
        self.save()

    def remove_action(self, key, parent_key=None):
        """アクションを削除"""
        container = self._get_action_container(parent_key, require_exists=False)
        if not container:
            return

        if key.upper() in container:
            del container[key.upper()]

        self.save()

    def update_action(self, old_key, old_parent_key, new_key, label, action_type, params, new_parent_key=None):
        """既存アクションを更新"""
        self._validate_single_key(new_key)
        self._validate_label(label)

        old_container = self._get_action_container(old_parent_key)
        old_normalized_key = old_key.upper()
        node = old_container.get(old_normalized_key)
        if not node:
            raise ValueError("編集対象のアクションが見つかりません")

        new_container = self._get_action_container(new_parent_key)
        new_normalized_key = new_key.upper()

        if old_container is not new_container or old_normalized_key != new_normalized_key:
            if new_normalized_key in new_container:
                raise ValueError(f"キー '{new_normalized_key}' は既に使用されています")

        del old_container[old_normalized_key]
        new_container[new_normalized_key] = ActionNode(
            key=new_key,
            label=label,
            action_type=action_type,
            params=params,
        )
        self.save()

    def get_all_actions_flat(self):
        """全アクションをフラットなリストで返す（設定UI用）"""
        result = []
        for node in self.root_actions.values():
            if node.is_group:
                for child in node.children.values():
                    result.append({
                        "key_display": f"{node.key}→{child.key}",
                        "label": child.label,
                        "type": child.action_type,
                        "params": child.params,
                        "parent_key": node.key,
                        "child_key": child.key,
                    })
            else:
                result.append({
                    "key_display": node.key,
                    "label": node.label,
                    "type": node.action_type,
                    "params": node.params,
                    "parent_key": None,
                    "child_key": node.key,
                })
        return result

    def _get_action_container(self, parent_key=None, require_exists=True):
        """対象階層のアクション辞書を返す"""
        if not parent_key:
            return self.root_actions

        parent = self.root_actions.get(parent_key.upper())
        if parent and parent.is_group:
            return parent.children

        if require_exists:
            raise ValueError(f"カテゴリ '{parent_key}' が見つかりません")
        return None

    @staticmethod
    def _validate_single_key(key):
        normalized_key = (key or "").strip().upper()
        if len(normalized_key) != 1:
            raise ValueError("キーは1文字で入力してください")

    @staticmethod
    def _validate_label(label):
        if not (label or "").strip():
            raise ValueError("名前を入力してください")
