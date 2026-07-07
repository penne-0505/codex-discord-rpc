from __future__ import annotations

from pathlib import Path
import os
import sqlite3
import subprocess

from codex_discord_rpc.project_detection import (
    distinct_projects,
    filter_recent_projects,
    iter_node_repl_candidates,
    is_codex_desktop_running,
    is_project_cwd,
    latest_codex_project_recency_ms,
    ProjectCandidate,
)


def _proc_entry(proc_root: Path, pid: int, cwd: Path, exe: str) -> None:
    proc_dir = proc_root / str(pid)
    proc_dir.mkdir()
    os.symlink(cwd, proc_dir / "cwd")
    os.symlink(exe, proc_dir / "exe")


def test_iter_node_repl_candidates_reads_project_cwd(tmp_path: Path) -> None:
    proc_root = tmp_path / "proc"
    proc_root.mkdir()
    project = tmp_path / "project"
    project.mkdir()
    _proc_entry(proc_root, 100, project, "/opt/codex-desktop/resources/node_repl")
    _proc_entry(proc_root, 101, Path("/opt/codex-desktop"), "/opt/codex-desktop/electron")

    candidates = iter_node_repl_candidates(proc_root)

    assert len(candidates) == 1
    assert candidates[0].cwd == project.resolve()


def test_distinct_projects_collapses_same_identity(tmp_path: Path) -> None:
    proc_root = tmp_path / "proc"
    proc_root.mkdir()
    project = tmp_path / "project"
    subdir = project / "subdir"
    subdir.mkdir(parents=True)
    subprocess.run(["git", "init"], cwd=project, check=True, stdout=subprocess.PIPE)
    _proc_entry(proc_root, 100, project, "/opt/codex-desktop/resources/node_repl")
    _proc_entry(proc_root, 101, subdir, "/opt/codex-desktop/resources/node_repl")

    candidates = iter_node_repl_candidates(proc_root)
    projects = distinct_projects(candidates)

    assert len(projects) == 1
    assert projects[0].identity == project.resolve()


def test_is_project_cwd_rejects_codex_desktop_internal_path() -> None:
    assert is_project_cwd(Path("/opt/codex-desktop")) is False


def test_is_codex_desktop_running_uses_electron_process_only(tmp_path: Path) -> None:
    proc_root = tmp_path / "proc"
    proc_root.mkdir()
    project = tmp_path / "project"
    project.mkdir()
    _proc_entry(proc_root, 100, project, "/opt/codex-desktop/resources/node_repl")

    assert is_codex_desktop_running(proc_root) is False

    _proc_entry(proc_root, 101, Path("/opt/codex-desktop"), "/opt/codex-desktop/electron")

    assert is_codex_desktop_running(proc_root) is True


def _codex_state_db(path: Path) -> None:
    with sqlite3.connect(path) as connection:
        connection.execute(
            """
            CREATE TABLE threads (
                id TEXT PRIMARY KEY,
                cwd TEXT NOT NULL,
                archived INTEGER NOT NULL DEFAULT 0,
                recency_at_ms INTEGER NOT NULL DEFAULT 0,
                updated_at_ms INTEGER NOT NULL DEFAULT 0,
                created_at_ms INTEGER,
                updated_at INTEGER NOT NULL DEFAULT 0,
                created_at INTEGER NOT NULL DEFAULT 0
            )
            """
        )


def test_latest_codex_project_recency_reads_identity_descendants(tmp_path: Path) -> None:
    db_path = tmp_path / "state.sqlite"
    project = tmp_path / "project"
    subdir = project / "subdir"
    subdir.mkdir(parents=True)
    _codex_state_db(db_path)
    with sqlite3.connect(db_path) as connection:
        connection.execute(
            "INSERT INTO threads (id, cwd, archived, recency_at_ms) VALUES (?, ?, ?, ?)",
            ("thread-1", str(subdir), 0, 1_700_000_000_000),
        )

    candidate = ProjectCandidate(pid=1, started_at=10, cwd=project, identity=project)

    assert latest_codex_project_recency_ms(candidate, db_path) == 1_700_000_000_000


def test_filter_recent_projects_drops_known_stale_candidates(tmp_path: Path) -> None:
    db_path = tmp_path / "state.sqlite"
    recent_project = tmp_path / "recent"
    stale_project = tmp_path / "stale"
    unknown_project = tmp_path / "unknown"
    for project in (recent_project, stale_project, unknown_project):
        project.mkdir()
    _codex_state_db(db_path)
    with sqlite3.connect(db_path) as connection:
        connection.executemany(
            "INSERT INTO threads (id, cwd, archived, recency_at_ms) VALUES (?, ?, ?, ?)",
            [
                ("recent", str(recent_project), 0, 2_000_000),
                ("stale", str(stale_project), 0, 1_000_000),
            ],
        )
    candidates = [
        ProjectCandidate(pid=1, started_at=10, cwd=recent_project, identity=recent_project),
        ProjectCandidate(pid=2, started_at=11, cwd=stale_project, identity=stale_project),
        ProjectCandidate(pid=3, started_at=12, cwd=unknown_project, identity=unknown_project),
    ]

    recent, stale_count = filter_recent_projects(
        candidates,
        ttl_minutes=10,
        db_path=db_path,
        now_ms=2_000_000,
    )

    assert [candidate.identity for candidate in recent] == [recent_project, unknown_project]
    assert stale_count == 1
