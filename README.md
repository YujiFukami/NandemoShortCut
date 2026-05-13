# なんでもショートカット

<p align="center">
  <a href="https://www.softex-celware.com/">
    <img src="softex-celwareロゴ 透過.png" alt="softex-celware logo" width="280">
  </a>
</p>

Windows で常駐し、ランチャーEXEやシステムトレイからショートカット画面を呼び出せるデスクトップアプリです。
日付コピー、定型文コピー、URL起動、ファイル起動、フォルダ作成、コマンド実行などをキー操作で実行できます。

開発者ホームページ: https://www.softex-celware.com/

解説ブログ:
https://www.softex-celware.com/post/nandemo-shortcut-windows-launcher

現在のバージョン: `v1.0.0`

## 主な機能

- `NandemoShortcutLauncher.exe` またはトレイメニューからメイン画面を表示
- 1文字キー、2段階キーによるショートカット実行
- URLを開く
- ファイルやフォルダを開く
- アクティブなエクスプローラー上でフォルダ作成
- 日付や定型文をクリップボードへコピー
- ファイルをクリップボードへコピーしてエクスプローラーへ貼り付け
- テキストの自動入力
- 設定画面からアクションやカテゴリを編集
- 二重起動防止

## 動作環境

- Windows 10 / 11
- Python 3.12 系で開発

## 配布版の使い方

1. 配布ZIPを任意の場所へ展開します。
2. `NandemoShortcut.exe` を実行します。
3. `NandemoShortcutLauncher.exe` を実行するか、システムトレイのメニューから `メイン画面を開く` を選びます。
4. 表示された画面でキーを押してアクションを実行します。

初回起動時に Windows SmartScreen やウイルス対策ソフトの警告が表示される場合があります。

## タスクバーから素早く呼び出す

`NandemoShortcutLauncher.exe` をWindowsのタスクバーにピン留めしておくと、`Windowsキー + 数字キー` でショートカット画面を呼び出せます。

例:

- タスクバーの左から1番目に登録: `Windows + 1`
- タスクバーの左から2番目に登録: `Windows + 2`

本体の `NandemoShortcut.exe` は常駐用、`NandemoShortcutLauncher.exe` は呼び出し用として使う想定です。
ランチャーをタスクバーに置いておくと、作業中の画面を切り替えずにショートカット一覧を開けます。

タスクバーのアイコンが古い表示のままの場合は、いったんピン留めを解除して、最新の `NandemoShortcutLauncher.exe` を右クリックして再度ピン留めしてください。それでも変わらない場合は、ExplorerまたはPCを再起動してください。

Windows 11で右クリックメニューに `タスクバーにピン留めする` が見当たらない場合は、`その他のオプションを確認` を開いてください。従来の右クリックメニュー側に表示されることがあります。

## 初期ショートカット

- `T -> A`: `ありがとうございます。` をコピー
- `T -> Y`: `よろしくお願いします。` をコピー
- `O -> B`: `バックアップ` フォルダを作成
- `O -> T`: `テンプレート` フォルダを作成
- `O -> O`: `オリジナル` フォルダを作成
- `U -> G`: Googleを開く
- `U -> M`: Gmailを開く
- `U -> B`: 解説ブログを開く
- `D -> D`: 今日の日付を `YYYYMMDD` 形式でコピー

## 設定画面

- システムトレイのメニューから開けます
- メイン画面表示中に `S` キー、または `設定` ボタンから開けます
- アクションの追加、編集、削除とカテゴリの追加、編集、削除ができます
- 設定内容は `config.json` に保存されます
- 左側でカテゴリを選んだ状態でアクションを追加すると、追加画面のカテゴリ欄にそのカテゴリが最初から選択されます
- アクションは必ずカテゴリ内に作成します。トップ階層へ直接アクションを追加する方式は使いません
- `読み込み` から別の `config.json` を読み込めます。読み込み前に現在設定のバックアップを作成します
- `書き出し` から現在の設定を任意の場所へ保存できます
- `設定フォルダ` から現在使っている設定ファイルのフォルダを開けます
- `使い方`、`開発元`、`GitHub` ボタンから関連ページを開けます

## 設定ファイル

設定は `config.json` で管理します。

- EXE実行時: EXEと同じフォルダの `config.json`
- 開発時: プロジェクト直下の `config.json`

公開リポジトリには個人環境向けのパスやURLを含めず、公開用の初期設定だけを保持します。

## 起動の流れ

- `NandemoShortcut.exe` はメインアプリとして常駐します
- `NandemoShortcutLauncher.exe` は、常駐中のアプリへメイン画面表示を依頼します
- 既に常駐中の状態でメインEXEを再実行した場合も、既存プロセスのメイン画面を表示します
- トレイメニューの `メイン画面を開く` からも同じ画面を表示できます

## 開発時の起動

依存関係をインストールします。

```bash
python -m pip install -r requirements.txt
```

アプリを起動します。

```bash
python main.py
```

## EXEビルド

PyInstallerを使ってビルドします。

```bash
python -m PyInstaller NandemoShortcut.spec --noconfirm
```

または `build_exe.bat` を実行します。

生成物:

- `dist/NandemoShortcut.exe`
- `dist/NandemoShortcutLauncher.exe`

配布ZIPには、上記2つのEXEに加えて、公開用 `config.json`、README、ライセンス表記、必要に応じて `NandemoShortcut.ico` を同梱してください。

## リポジトリに含めないもの

- `build/`
- `dist/`
- `__pycache__/`
- `開発者用/`
- `オリジナル/`
- 配布用ZIP
- EXEを入れた配布用フォルダ
- 個人用ショートカットやリンク集

## ライセンス

このプロジェクト本体は MIT License です。
詳細は [LICENSE](LICENSE) を参照してください。

依存ライブラリの表記は [THIRD_PARTY_NOTICES.md](THIRD_PARTY_NOTICES.md) を参照してください。
