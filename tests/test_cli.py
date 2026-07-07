from __future__ import annotations

from pathlib import Path
import sys
import types

from codex_discord_rpc.cli import main
from codex_discord_rpc.project_detection import ProjectCandidate


class FakePresence:
    instances: list["FakePresence"] = []

    def __init__(self, client_id: str) -> None:
        self.client_id = client_id
        self.connected = False
        self.cleared = False
        self.updates: list[dict[str, object]] = []
        self.instances.append(self)

    def connect(self) -> None:
        self.connected = True

    def update(self, **kwargs: object) -> None:
        self.updates.append(kwargs)

    def clear(self) -> None:
        self.cleared = True


def test_run_once_updates_presence_with_fake_rpc(
    tmp_path: Path,
    monkeypatch,
) -> None:
    module = types.ModuleType("pypresence")
    module.Presence = FakePresence
    monkeypatch.setitem(sys.modules, "pypresence", module)
    FakePresence.instances.clear()

    result = main(
        [
            "--config",
            str(tmp_path / "missing-config.toml"),
            "run",
            "--repo",
            ".",
            "--client-id",
            "123",
            "--once",
        ]
    )

    assert result == 0
    instance = FakePresence.instances[0]
    assert instance.client_id == "123"
    assert instance.connected is True
    assert instance.cleared is True
    assert instance.updates[0]["details"] == "codex-discord-rpc で作業中"


def test_monitor_once_uses_multiple_project_payload(
    tmp_path: Path,
    monkeypatch,
) -> None:
    module = types.ModuleType("pypresence")
    module.Presence = FakePresence
    monkeypatch.setitem(sys.modules, "pypresence", module)
    FakePresence.instances.clear()
    project_a = tmp_path / "a"
    project_b = tmp_path / "b"
    project_a.mkdir()
    project_b.mkdir()
    monkeypatch.setattr(
        "codex_discord_rpc.cli.iter_node_repl_candidates",
        lambda: [
            ProjectCandidate(pid=1, started_at=10, cwd=project_a, identity=project_a),
            ProjectCandidate(pid=2, started_at=11, cwd=project_b, identity=project_b),
        ],
    )

    result = main(
        [
            "--config",
            str(tmp_path / "missing-config.toml"),
            "monitor",
            "--client-id",
            "123",
            "--once",
        ]
    )

    assert result == 0
    instance = FakePresence.instances[0]
    assert instance.updates[0]["details"] == "2個のCodexプロジェクトで作業中"
    assert instance.updates[0]["state"] == "複数プロジェクト"
    assert "buttons" not in instance.updates[0]
