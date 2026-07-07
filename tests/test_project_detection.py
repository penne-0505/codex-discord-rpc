from __future__ import annotations

from pathlib import Path
import os
import subprocess

from codex_discord_rpc.project_detection import (
    distinct_projects,
    iter_node_repl_candidates,
    is_project_cwd,
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
