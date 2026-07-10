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

Codex Desktopのprojectを自動検出して反映する場合:

```bash
uv run codex-discord-rpc monitor
```

常駐serviceとして導入する場合:

```bash
uv run codex-discord-rpc doctor
./scripts/install-user-service.sh --dry-run
./scripts/install-user-service.sh --enable-now
systemctl --user status codex-discord-rpc.service
```

Discord Desktopが後から起動した場合や再起動した場合も、monitorが内部で再接続します。checkoutを移動した場合や
`.venv`を作り直した場合はinstallerを再実行してください。停止・rollbackは次を使います。

```bash
./scripts/install-user-service.sh --disable-now
```

フェーズ更新:

```bash
uv run codex-discord-rpc set-phase editing
uv run codex-discord-rpc set-phase running_tests
```

project pathを明示する場合:

```bash
uv run codex-discord-rpc set-project /path/to/project
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
