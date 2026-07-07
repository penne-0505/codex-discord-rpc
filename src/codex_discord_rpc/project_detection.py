from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
import os
import sqlite3
import subprocess
import time


NODE_REPL_EXE_SUFFIX = "/opt/codex-desktop/resources/node_repl"
CODEX_DESKTOP_ELECTRON_EXE = "/opt/codex-desktop/electron"
CODEX_STATE_DB = Path.home() / ".codex" / "state_5.sqlite"


@dataclass(frozen=True)
class ProjectCandidate:
    pid: int
    started_at: int
    cwd: Path
    identity: Path


def _read_link(path: Path) -> str | None:
    try:
        return os.readlink(path)
    except OSError:
        return None


def _proc_started_at(proc_dir: Path) -> int:
    try:
        return int(proc_dir.stat().st_mtime)
    except OSError:
        return 0


def _git_root(path: Path) -> Path | None:
    try:
        result = subprocess.run(
            ["git", "rev-parse", "--show-toplevel"],
            cwd=path,
            check=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.DEVNULL,
            text=True,
        )
    except (FileNotFoundError, subprocess.CalledProcessError, OSError):
        return None
    output = result.stdout.strip()
    return Path(output).resolve() if output else None


def _excluded_prefixes() -> tuple[Path, ...]:
    home = Path.home()
    return (
        Path("/opt/codex-desktop"),
        home / ".codex" / "plugins" / "cache",
        home / ".cache" / "codex-runtimes",
        home / ".npm" / "_npx",
        home / ".local" / "share" / "uv",
    )


def is_project_cwd(path: Path) -> bool:
    try:
        resolved = path.expanduser().resolve()
    except OSError:
        return False
    for prefix in _excluded_prefixes():
        try:
            resolved.relative_to(prefix)
            return False
        except ValueError:
            continue
    return resolved.exists() and resolved.is_dir()


def project_identity(path: Path) -> Path:
    resolved = path.expanduser().resolve()
    return _git_root(resolved) or resolved


def iter_node_repl_candidates(proc_root: Path = Path("/proc")) -> list[ProjectCandidate]:
    candidates: list[ProjectCandidate] = []
    for proc_dir in proc_root.iterdir():
        if not proc_dir.name.isdigit():
            continue
        exe = _read_link(proc_dir / "exe")
        if exe is None or not exe.endswith(NODE_REPL_EXE_SUFFIX):
            continue
        cwd_raw = _read_link(proc_dir / "cwd")
        if cwd_raw is None:
            continue
        cwd = Path(cwd_raw)
        if not is_project_cwd(cwd):
            continue
        candidates.append(
            ProjectCandidate(
                pid=int(proc_dir.name),
                started_at=_proc_started_at(proc_dir),
                cwd=cwd.resolve(),
                identity=project_identity(cwd),
            )
        )
    return candidates


def is_codex_desktop_running(proc_root: Path = Path("/proc")) -> bool:
    for proc_dir in proc_root.iterdir():
        if not proc_dir.name.isdigit():
            continue
        exe = _read_link(proc_dir / "exe")
        if exe == CODEX_DESKTOP_ELECTRON_EXE:
            return True
    return False


def distinct_projects(candidates: list[ProjectCandidate]) -> list[ProjectCandidate]:
    by_identity: dict[Path, ProjectCandidate] = {}
    for candidate in candidates:
        current = by_identity.get(candidate.identity)
        if current is None or candidate.started_at > current.started_at:
            by_identity[candidate.identity] = candidate
    return sorted(by_identity.values(), key=lambda item: item.started_at, reverse=True)


def latest_codex_project_recency_ms(
    candidate: ProjectCandidate,
    db_path: Path = CODEX_STATE_DB,
) -> int | None:
    if not db_path.exists():
        return None

    cwd = str(candidate.cwd)
    identity = str(candidate.identity)
    identity_prefix = f"{identity}/%"
    query = """
        SELECT max(
            coalesce(
                nullif(recency_at_ms, 0),
                nullif(updated_at_ms, 0),
                nullif(created_at_ms, 0),
                nullif(updated_at, 0) * 1000,
                nullif(created_at, 0) * 1000
            )
        )
        FROM threads
        WHERE archived = 0
          AND (cwd = ? OR cwd = ? OR cwd LIKE ?)
    """
    try:
        with sqlite3.connect(f"file:{db_path}?mode=ro", uri=True) as connection:
            row = connection.execute(query, (cwd, identity, identity_prefix)).fetchone()
    except sqlite3.Error:
        return None
    value = row[0] if row else None
    return int(value) if value else None


def filter_recent_projects(
    candidates: list[ProjectCandidate],
    ttl_minutes: int,
    db_path: Path = CODEX_STATE_DB,
    now_ms: int | None = None,
) -> tuple[list[ProjectCandidate], int]:
    if ttl_minutes <= 0:
        return candidates, 0

    now = now_ms if now_ms is not None else int(time.time() * 1000)
    ttl_ms = ttl_minutes * 60 * 1000
    recent: list[ProjectCandidate] = []
    stale_count = 0
    for candidate in candidates:
        recency_ms = latest_codex_project_recency_ms(candidate, db_path)
        if recency_ms is not None and now - recency_ms > ttl_ms:
            stale_count += 1
            continue
        recent.append(candidate)
    return recent, stale_count
