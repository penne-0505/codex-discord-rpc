# Codex Discord RPC

A small Python CLI that publishes your current Codex work state to Discord Rich Presence.

It shows a compact, editor-like presence: repository, phase, and elapsed time. When the current Git remote can be normalized to a GitHub repository URL, it also adds a `View Repository` button.

```text
Codex (Desktop)
Working on codex-discord-rpc
Editing
elapsed time

[View Repository]
```

Japanese labels are used by default. English labels can be enabled in the config.
The activity name sent to Discord is `Codex (Desktop)`.
If Discord still shows a different top-level title, rename the Discord application in the Developer Portal; some clients prefer the application name for that line.

## Features

- Discord Rich Presence for local Codex sessions
- Repository name, work phase, and timer display
- Optional GitHub repository button
- Japanese and English labels
- Dry-run JSON rendering without connecting to Discord
- Linux project auto-detection for Codex Desktop sessions
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
large_image_key = ""
auto_detect_projects = true
repo_path = "."
phase = "editing"
refresh_interval_seconds = 15
state_file = ""
```

Set `language = "en"` to use English display labels.

Set `large_image_key` to a Discord Rich Presence asset key when you want a large image in the presence card. Leave it empty to omit the image.

When `state_file` is empty, the default state file is:

```text
~/.local/state/codex-discord-rpc/state.json
```

`auto_detect_projects` enables Linux `/proc` based Codex Desktop project detection. It looks for Codex Desktop `node_repl` helper processes and uses their working directories as project candidates.

## Usage

Render the payload without connecting to Discord:

```bash
uv run codex-discord-rpc render --repo .
```

Start Rich Presence updates:

```bash
uv run codex-discord-rpc run --repo .
```

Monitor Codex Desktop projects automatically:

```bash
uv run codex-discord-rpc monitor
```

`monitor` writes concise status changes to stderr, including whether projects were detected, whether multiple projects were aggregated, and when Rich Presence is updated or cleared. When run under systemd, these messages are available in the user journal.

When one Codex project is detected, the project name is displayed. When multiple distinct projects are detected, the presence uses an aggregate display and omits repository buttons:

```text
Codex (Desktop)
3個のCodexプロジェクトで作業中
複数プロジェクト
elapsed time
```

Update the current phase:

```bash
uv run codex-discord-rpc set-phase running_tests
```

Set an explicit project path:

```bash
uv run codex-discord-rpc set-project /path/to/project
```

## systemd user service

For always-on local use, run `monitor` as a user service.

Example `~/.config/systemd/user/codex-discord-rpc.service`:

```ini
[Unit]
Description=Codex Discord Rich Presence

[Service]
Type=simple
WorkingDirectory=/path/to/codex-discord-rpc
ExecStart=/path/to/codex-discord-rpc/.venv/bin/codex-discord-rpc monitor
Restart=on-failure
RestartSec=5

[Install]
WantedBy=default.target
```

Enable it:

```bash
systemctl --user daemon-reload
systemctl --user enable --now codex-discord-rpc.service
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
