from __future__ import annotations

from pathlib import Path

from codex_discord_rpc.state import load_state, write_repo_path, write_state


def test_set_phase_preserves_explicit_repo_path(tmp_path: Path) -> None:
    state_path = tmp_path / "state.json"
    project = tmp_path / "project"
    project.mkdir()

    write_repo_path(state_path, str(project), started_at=100)
    write_state(state_path, "running_tests", started_at=200)
    state = load_state(state_path, "editing", 300)

    assert state.phase == "running_tests"
    assert state.started_at == 200
    assert state.repo_path == str(project.resolve())
