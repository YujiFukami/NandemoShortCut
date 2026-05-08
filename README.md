# なんでもショートカット

<p align="center">
  <a href="https://www.softex-celware.com/">
    <img src="softex-celwareロゴ 透過.png" alt="softex-celware logo" width="280">
  </a>
</p>

Windows で常駐し、ランチャーEXEやシステムトレイからショートカット画面を呼び出せるデスクトップアプリです。
日付コピー、定型文コピー、URL起動、ファイル起動、フォルダ作成、コマンド実行などをキー操作で実行できます。

開発者ホームページ: https://www.softex-celware.com/

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

## 初期ショートカット

- `D`: 今日の日付を `YYYYMMDD` 形式でコピー
- `O -> B`: `バックアップ` フォルダを作成
- `O -> T`: `テンプレート` フォルダを作成
- `O -> O`: `オリジナル` フォルダを作成
- `U -> G`: Googleを開く
- `U -> M`: Gmailを開く

## 設定画面

- システムトレイのメニューから開けます
- メイン画面表示中に `S` キー、または `設定` ボタンから開けます
- アクションの追加、編集、削除とカテゴリの追加、編集、削除ができます
- 設定内容は `config.json` に保存されます

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

配布ZIPには、上記2つのEXEに加えて、公開用 `config.json`、README、ライセンス表記を同梱してください。

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
