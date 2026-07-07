# Quickstart

## 1. 利用開始

```bash
uv sync --extra dev
uv run codex-discord-rpc init
```

`~/.config/codex-discord-rpc/config.toml` の `client_id` にDiscordアプリケーションのclient IDを設定します。

## 2. 表示確認

Discordに接続せず、Rich Presence payloadだけ確認します。

```bash
uv run codex-discord-rpc render --repo .
```

Discord Desktopへ反映する場合:

```bash
uv run codex-discord-rpc run --repo .
```

フェーズ更新:

```bash
uv run codex-discord-rpc set-phase editing
uv run codex-discord-rpc set-phase running_tests
```

## 3. 開発時に読むファイル

- [AGENTS.md](AGENTS.md)
- [TODO.md](TODO.md)
- [_docs/documentation_guide.md](_docs/documentation_guide.md)
- [_docs/intent/Core/codex-rich-presence/decision.md](_docs/intent/Core/codex-rich-presence/decision.md)
- [_docs/qa/Core/codex-rich-presence/test-plan.md](_docs/qa/Core/codex-rich-presence/test-plan.md)

## 4. 検証コマンド

```bash
uv sync --extra dev
uv run pytest
uv run ruff check .
./scripts/check-docs.sh
```
