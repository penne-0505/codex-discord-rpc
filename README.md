# Codex Discord RPC

A small Python CLI that publishes your current Codex work state to Discord Rich Presence.

It shows a compact, editor-like presence: repository, phase, and elapsed time. When the current Git remote can be normalized to a GitHub repository URL, it also adds a `View Repository` button.

```text
Codex
Working on codex-discord-rpc
Editing
elapsed time

[View Repository]
```

Japanese labels are used by default. English labels can be enabled in the config.

## Features

- Discord Rich Presence for local Codex sessions
- Repository name, work phase, and timer display
- Optional GitHub repository button
- Japanese and English labels
- Dry-run JSON rendering without connecting to Discord
- File-based phase updates for simple external automation

## Privacy

Codex Discord RPC intentionally keeps the displayed information narrow.

It does not display:

- file names
- branch names
- prompt text
- command text
- task details
- secrets or credentials

The repository button is only generated for recognized GitHub remotes:

- `git@github.com:owner/repo.git`
- `https://github.com/owner/repo.git`
- `https://github.com/owner/repo`

Other remotes do not produce a button.

## Requirements

- Python 3.11 or later
- [uv](https://docs.astral.sh/uv/)
- Discord Desktop
- A Discord application client ID

Create an application in the Discord Developer Portal and use its client ID in the local config.

## Installation

From a local checkout:

```bash
uv sync
uv run codex-discord-rpc --help
```

For development tools:

```bash
uv sync --extra dev
```

## Configuration

Create the default config file:

```bash
uv run codex-discord-rpc init
```

The default path is:

```text
~/.config/codex-discord-rpc/config.toml
```

Example:

```toml
enabled = true
language = "ja"
client_id = "YOUR_DISCORD_APPLICATION_CLIENT_ID"
show_repository_button = true
show_timer = true
repo_path = "."
phase = "editing"
refresh_interval_seconds = 15
state_file = ""
```

Set `language = "en"` to use English display labels.

When `state_file` is empty, the default state file is:

```text
~/.local/state/codex-discord-rpc/state.json
```

## Usage

Render the payload without connecting to Discord:

```bash
uv run codex-discord-rpc render --repo .
```

Start Rich Presence updates:

```bash
uv run codex-discord-rpc run --repo .
```

Update the current phase:

```bash
uv run codex-discord-rpc set-phase running_tests
```

List supported phases:

```bash
uv run codex-discord-rpc phases
```

Default Japanese phase labels:

```text
idle               待機中
reading_context    文脈を確認中
editing            編集中
running_commands   コマンド実行中
running_tests      テスト実行中
reviewing_changes  変更を確認中
waiting_for_input  入力待ち
```

English labels:

```bash
uv run codex-discord-rpc phases --language en
```

## Development

```bash
uv sync --extra dev
uv run pytest
uv run ruff check .
./scripts/check-docs.sh
```

## License

MIT License. See [LICENSE.txt](LICENSE.txt).
