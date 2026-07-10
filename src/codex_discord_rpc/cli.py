from __future__ import annotations

import argparse
import json
from pathlib import Path
import signal
import sys
import threading
import time

from .config import Config, default_config_path, load_config, write_default_config
from .git_info import get_repository_info
from .phases import phase_table
from .presence import build_idle_payload, build_multi_project_payload, build_payload, render_payload
from .project_detection import (
    distinct_projects,
    filter_recent_projects,
    is_codex_desktop_running,
    iter_node_repl_candidates,
)
from .rpc import BackoffPolicy, CoordinatorEvent, PermanentPresenceError, PresenceCoordinator
from .state import default_state_path, load_state, write_repo_path, write_state


def _log(message: str) -> None:
    print(f"[codex-discord-rpc] {message}", file=sys.stderr, flush=True)


def _check(status: str, message: str) -> None:
    print(f"[{status}] {message}")


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


def cmd_set_project(args: argparse.Namespace) -> int:
    config = _config_from_args(args)
    state_path = Path(config.state_file).expanduser() if config.state_file else default_state_path()
    path = write_repo_path(state_path, args.path)
    print(path)
    return 0


def cmd_render(args: argparse.Namespace) -> int:
    config = _config_from_args(args)
    payload = render_payload(config, args.repo or config.repo_path)
    print(json.dumps(payload.as_rpc_kwargs(), ensure_ascii=False, indent=2))
    return 0


def _presence_factory(config: Config):
    if not config.enabled:
        print("codex-discord-rpc is disabled by config", file=sys.stderr)
        return None, 0
    if not config.client_id:
        print(
            f"client_id is required. Run `codex-discord-rpc init` and edit {default_config_path()}",
            file=sys.stderr,
        )
        return None, 2

    try:
        from pypresence import Presence
    except ImportError as exc:
        print(f"pypresence is not installed: {exc}", file=sys.stderr)
        return None, 2

    return (
        lambda: Presence(
            config.client_id,
            connection_timeout=config.rpc_timeout_seconds,
            response_timeout=config.rpc_timeout_seconds,
        ),
        0,
    )


def _connect_presence(config: Config):
    factory, status = _presence_factory(config)
    if factory is None:
        return None, status
    rpc = factory()
    try:
        rpc.connect()
    except Exception as exc:  # pypresence raises library-specific exceptions for local RPC failures.
        print(f"failed to connect to Discord Rich Presence: {exc}", file=sys.stderr)
        return None, 3
    return rpc, 0


def cmd_doctor(args: argparse.Namespace) -> int:
    config = _config_from_args(args)
    failures = 0
    config_path = Path(args.config).expanduser() if args.config else default_config_path()
    if config_path.exists():
        _check("PASS", f"config exists: {config_path}")
    else:
        failures += 1
        _check("FAIL", f"config is missing: {config_path}")

    if config.client_id:
        _check("PASS", "Discord client ID is configured")
    else:
        failures += 1
        _check("FAIL", "Discord client ID is missing")

    try:
        import pypresence  # noqa: F401
    except ImportError:
        failures += 1
        _check("FAIL", "pypresence is unavailable")
    else:
        _check("PASS", "pypresence is available")

    if Path("/proc").is_dir():
        _check("PASS", "Linux process metadata is available")
    else:
        failures += 1
        _check("FAIL", "Linux /proc is unavailable")

    _check("PASS", f"Python runtime is executable: {Path(sys.executable).resolve()}")
    _check("INFO", "Discord Desktop may be offline; monitor will retry without exiting")
    return 2 if failures else 0


def cmd_run(args: argparse.Namespace) -> int:
    config = _config_from_args(args)
    rpc, status = _connect_presence(config)
    if rpc is None:
        return status

    repository = get_repository_info(args.repo or config.repo_path)
    state_path = Path(config.state_file).expanduser() if config.state_file else default_state_path()
    started_at = int(time.time())

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


def _monitor_payload(config: Config, started_at: int):
    state_path = Path(config.state_file).expanduser() if config.state_file else default_state_path()
    runtime_state = load_state(state_path, config.phase, started_at)

    if runtime_state.repo_path:
        repository = get_repository_info(runtime_state.repo_path)
        return (
            build_payload(config, repository, runtime_state.phase, runtime_state.started_at),
            f"state-project:{repository.root}",
        )

    if config.auto_detect_projects:
        candidates, stale_count = filter_recent_projects(
            iter_node_repl_candidates(),
            config.active_project_ttl_minutes,
        )
        projects = distinct_projects(candidates)
        stale_status = f":stale={stale_count}" if stale_count else ""
        if len(projects) == 1:
            repository = get_repository_info(projects[0].identity)
            return (
                build_payload(config, repository, runtime_state.phase, projects[0].started_at),
                f"detected-project:{repository.root}{stale_status}",
            )
        if len(projects) > 1:
            roots = ", ".join(str(project.identity) for project in projects[:5])
            suffix = "" if len(projects) <= 5 else f", +{len(projects) - 5} more"
            return (
                build_multi_project_payload(config, len(projects), started_at),
                f"detected-multiple:{len(projects)}:{roots}{suffix}{stale_status}",
            )
        if is_codex_desktop_running():
            return (
                build_idle_payload(config, started_at),
                f"idle{stale_status}",
            )
        return None, f"no-projects{stale_status}"

    repository = get_repository_info(config.repo_path)
    return (
        build_payload(config, repository, runtime_state.phase, runtime_state.started_at),
        f"config-project:{repository.root}",
    )


def _log_monitor_status(status_key: str) -> None:
    status, _, stale_part = status_key.partition(":stale=")
    stale_suffix = f"; ignored stale projects={stale_part}" if stale_part else ""
    if status == "no-projects":
        _log(f"no Codex projects detected{stale_suffix}")
    elif status == "idle":
        _log(f"Codex Desktop is running without an active project{stale_suffix}")
    elif status_key.startswith("detected-project:"):
        project = Path(status.removeprefix("detected-project:")).name
        _log(f"detected Codex project {project}{stale_suffix}")
    elif status.startswith("detected-multiple:"):
        _, count, _roots = status.split(":", 2)
        _log(f"detected {count} Codex projects{stale_suffix}")
    elif status.startswith("state-project:"):
        project = Path(status.removeprefix("state-project:")).name
        _log(f"using explicit state project {project}")
    elif status.startswith("config-project:"):
        project = Path(status.removeprefix("config-project:")).name
        _log(f"using configured fallback project {project}")


def _log_coordinator_events(events: tuple[CoordinatorEvent, ...]) -> None:
    for event in events:
        if event.kind == "connected":
            _log("connected to Discord IPC")
        elif event.kind == "retry":
            retry = f"{event.retry_seconds:g}" if event.retry_seconds is not None else "unknown"
            _log(f"Discord IPC unavailable; retry in {retry}s ({event.error_type})")
        elif event.kind == "updated" and not event.health_refresh:
            _log("updated Discord Rich Presence")
        elif event.kind == "cleared":
            _log("cleared Discord Rich Presence")


def cmd_monitor(args: argparse.Namespace) -> int:
    config = _config_from_args(args)
    started_at = int(time.time())
    _log(
        "monitor started "
        f"auto_detect_projects={config.auto_detect_projects} "
        f"active_project_ttl_minutes={config.active_project_ttl_minutes} "
        f"interval={config.refresh_interval_seconds}s"
    )
    initial_payload, initial_status = _monitor_payload(config, started_at)
    _log_monitor_status(initial_status)

    factory, status = _presence_factory(config)
    if factory is None:
        return status

    # intent: INV-012 (Core/codex-rich-presence) — Discord Desktop lifecycle is
    # recovered inside monitor; systemd remains a supervisor for process faults.
    coordinator = PresenceCoordinator(
        factory,
        backoff=BackoffPolicy(
            initial_delay=config.reconnect_initial_seconds,
            maximum_delay=config.reconnect_max_seconds,
        ),
        refresh_interval=config.refresh_interval_seconds,
    )
    coordinator.set_desired(
        initial_payload.as_rpc_kwargs() if initial_payload is not None else None
    )
    stop_event = threading.Event()
    previous_handlers: dict[int, object] = {}

    def request_stop(signum: int, _frame: object) -> None:
        if not stop_event.is_set():
            _log(f"received signal {signum}; shutting down")
        stop_event.set()

    try:
        last_status: str | None = initial_status
        for signum in (signal.SIGINT, signal.SIGTERM):
            previous_handlers[signum] = signal.signal(signum, request_stop)
        now = time.monotonic()
        next_scan_at = now + config.refresh_interval_seconds
        while not stop_event.is_set():
            try:
                events = coordinator.pump(now)
            except PermanentPresenceError as error:
                _log(f"permanent Discord RPC failure ({error.error_type})")
                return 4
            _log_coordinator_events(events)
            if args.once:
                return 3 if any(event.kind == "retry" for event in events) else 0

            wake_at = coordinator.next_action_at(next_scan_at)
            stop_event.wait(max(0.05, wake_at - time.monotonic()))
            if stop_event.is_set():
                break

            now = time.monotonic()
            if now >= next_scan_at:
                payload, status_key = _monitor_payload(config, started_at)
                if status_key != last_status:
                    _log_monitor_status(status_key)
                    last_status = status_key
                coordinator.set_desired(payload.as_rpc_kwargs() if payload is not None else None)
                next_scan_at = now + config.refresh_interval_seconds
        return 0
    finally:
        clear_confirmed = coordinator.shutdown()
        if clear_confirmed:
            _log("cleared Discord Rich Presence during shutdown")
        else:
            _log("monitor stopped; no clear acknowledgement was available")
        for signum, previous_handler in previous_handlers.items():
            signal.signal(signum, previous_handler)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="codex-discord-rpc",
        description="Discord Rich Presence helper for Codex sessions.",
    )
    parser.add_argument("--config", help="Path to config.toml")

    subcommands = parser.add_subparsers(dest="command", required=True)

    doctor_parser = subcommands.add_parser(
        "doctor",
        help="Check config and local runtime without requiring Discord Desktop",
    )
    doctor_parser.set_defaults(func=cmd_doctor)

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

    set_project_parser = subcommands.add_parser(
        "set-project",
        help="Write an explicit project path to state.json",
    )
    set_project_parser.add_argument("path")
    set_project_parser.add_argument("--language", choices=["ja", "en"])
    set_project_parser.set_defaults(func=cmd_set_project)

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

    monitor_parser = subcommands.add_parser(
        "monitor",
        help="Auto-detect Codex Desktop projects and update Rich Presence",
    )
    monitor_parser.add_argument("--repo", help="Fallback repository path")
    monitor_parser.add_argument("--phase", help="Initial phase key")
    monitor_parser.add_argument("--language", choices=["ja", "en"])
    monitor_parser.add_argument("--client-id", help="Discord application client ID")
    monitor_parser.add_argument("--once", action="store_true", help="Update once and exit")
    monitor_parser.set_defaults(func=cmd_monitor)

    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    try:
        return int(args.func(args))
    except ValueError as error:
        print(f"configuration error: {error}", file=sys.stderr)
        return 2
    except OSError as error:
        print(f"runtime error ({type(error).__name__})", file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
