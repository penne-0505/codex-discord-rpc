# Codex Discord RPC

Codexで作業している状態をDiscord Rich Presenceに表示する小さなPython CLIです。

基本表示は、事前に決めた方針どおり **repo + phase + timer** に絞っています。GitHub remote から安全にURLを作れる場合だけ、DiscordのRich Presenceボタンとして `リポジトリを見る` を出します。

```text
Codex
codex-discord-rpc で作業中
編集中
経過時間

[リポジトリを見る]
```

ファイル名、branch名、プロンプト本文、コマンド内容は表示しません。

## セットアップ

```bash
uv sync --extra dev
uv run codex-discord-rpc init
```

作成された設定ファイルを開き、Discord Developer Portalで作成したアプリケーションの client ID を設定します。

```toml
client_id = "YOUR_DISCORD_APPLICATION_CLIENT_ID"
language = "ja"
show_repository_button = true
show_timer = true
```

## 使い方

現在のrepoでpayloadだけ確認する場合:

```bash
uv run codex-discord-rpc render --repo .
```

Discord DesktopへRich Presenceを送る場合:

```bash
uv run codex-discord-rpc run --repo .
```

作業フェーズを更新する場合:

```bash
uv run codex-discord-rpc set-phase running_tests
```

対応フェーズ:

```text
idle              待機中
reading_context   文脈を確認中
editing           編集中
running_commands  コマンド実行中
running_tests     テスト実行中
reviewing_changes 変更を確認中
waiting_for_input 入力待ち
```

英語表示に切り替える場合:

```toml
language = "en"
```

## 設定

デフォルトの設定ファイルは `~/.config/codex-discord-rpc/config.toml` です。

```toml
enabled = true
language = "ja"
client_id = ""
show_repository_button = true
show_timer = true
repo_path = "."
phase = "editing"
refresh_interval_seconds = 15
state_file = ""
```

`state_file` を空にすると、`~/.local/state/codex-discord-rpc/state.json` が使われます。

## 開発

```bash
uv sync --extra dev
uv run pytest
uv run ruff check .
./scripts/check-docs.sh
```

## ライセンス

このリポジトリは [MIT License](LICENSE.txt) の下でライセンスされています。
