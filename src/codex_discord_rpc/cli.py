from __future__ import annotations

import argparse
import json
from pathlib import Path
import sys
import time

from .config import Config, default_config_path, load_config, write_default_config
from .git_info import get_repository_info
from .phases import phase_table
from .presence import build_payload, render_payload
from .state import default_state_path, load_state, write_state


def _config_from_args(args: argparse.Namespace) -> Config:
    config = load_config(Path(args.config).expanduser() if args.config else None)
    values = config.__dict__ | {
        key: value
        for key, value in {
            "language": getattr(args, "language", None),
            "client_id": getattr(args, "client_id", None),
            "repo_path": getattr(args, "repo", None),
            "phase": getattr(args, "phase", None),
        }.items()
        if value is not None
    }
    return Config.from_mapping(values)


def cmd_init(args: argparse.Namespace) -> int:
    path = write_default_config(Path(args.path).expanduser() if args.path else None, args.force)
    print(path)
    return 0


def cmd_phases(args: argparse.Namespace) -> int:
    config = _config_from_args(args)
    for key, label in phase_table(config.language):
        print(f"{key}\t{label}")
    return 0


def cmd_set_phase(args: argparse.Namespace) -> int:
    config = _config_from_args(args)
    state_path = Path(config.state_file).expanduser() if config.state_file else default_state_path()
    path = write_state(state_path, args.phase)
    print(path)
    return 0


def cmd_render(args: argparse.Namespace) -> int:
    config = _config_from_args(args)
    payload = render_payload(config, args.repo or config.repo_path)
    print(json.dumps(payload.as_rpc_kwargs(), ensure_ascii=False, indent=2))
    return 0


def cmd_run(args: argparse.Namespace) -> int:
    config = _config_from_args(args)
    if not config.enabled:
        print("codex-discord-rpc is disabled by config", file=sys.stderr)
        return 0
    if not config.client_id:
        print(
            f"client_id is required. Run `codex-discord-rpc init` and edit {default_config_path()}",
            file=sys.stderr,
        )
        return 2

    try:
        from pypresence import Presence
    except ImportError as exc:
        print(f"pypresence is not installed: {exc}", file=sys.stderr)
        return 2

    repository = get_repository_info(args.repo or config.repo_path)
    state_path = Path(config.state_file).expanduser() if config.state_file else default_state_path()
    started_at = int(time.time())
    rpc = Presence(config.client_id)
    try:
        rpc.connect()
    except Exception as exc:  # pypresence raises library-specific exceptions for local RPC failures.
        print(f"failed to connect to Discord Rich Presence: {exc}", file=sys.stderr)
        return 3

    try:
        while True:
            runtime_state = load_state(state_path, config.phase, started_at)
            payload = build_payload(config, repository, runtime_state.phase, runtime_state.started_at)
            try:
                rpc.update(**payload.as_rpc_kwargs())
            except Exception as exc:
                print(f"failed to update Discord Rich Presence: {exc}", file=sys.stderr)
                return 3
            if args.once:
                rpc.clear()
                return 0
            time.sleep(config.refresh_interval_seconds)
    except KeyboardInterrupt:
        rpc.clear()
        return 0


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="codex-discord-rpc",
        description="Discord Rich Presence helper for Codex sessions.",
    )
    parser.add_argument("--config", help="Path to config.toml")

    subcommands = parser.add_subparsers(dest="command", required=True)

    init_parser = subcommands.add_parser("init", help="Create a default config file")
    init_parser.add_argument("--path", help="Config path to create")
    init_parser.add_argument("--force", action="store_true", help="Overwrite existing config")
    init_parser.set_defaults(func=cmd_init)

    phases_parser = subcommands.add_parser("phases", help="List supported phases")
    phases_parser.add_argument("--language", choices=["ja", "en"])
    phases_parser.set_defaults(func=cmd_phases)

    set_parser = subcommands.add_parser("set-phase", help="Write the current phase to state.json")
    set_parser.add_argument("phase")
    set_parser.add_argument("--language", choices=["ja", "en"])
    set_parser.set_defaults(func=cmd_set_phase)

    render_parser = subcommands.add_parser("render", help="Render the Discord payload as JSON")
    render_parser.add_argument("--repo", help="Repository path")
    render_parser.add_argument("--phase", help="Phase key")
    render_parser.add_argument("--language", choices=["ja", "en"])
    render_parser.set_defaults(func=cmd_render)

    run_parser = subcommands.add_parser("run", help="Connect to Discord and update Rich Presence")
    run_parser.add_argument("--repo", help="Repository path")
    run_parser.add_argument("--phase", help="Initial phase key")
    run_parser.add_argument("--language", choices=["ja", "en"])
    run_parser.add_argument("--client-id", help="Discord application client ID")
    run_parser.add_argument("--once", action="store_true", help="Update once and exit")
    run_parser.set_defaults(func=cmd_run)

    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    return int(args.func(args))


if __name__ == "__main__":
    raise SystemExit(main())
