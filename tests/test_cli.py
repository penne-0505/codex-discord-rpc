from __future__ import annotations

from pathlib import Path
import sys
import types

from codex_discord_rpc.cli import main
from codex_discord_rpc.project_detection import ProjectCandidate


class FakePresence:
    instances: list["FakePresence"] = []

    def __init__(self, client_id: str, **_kwargs: object) -> None:
        self.client_id = client_id
        self.connected = False
        self.cleared = False
        self.closed = False
        self.updates: list[dict[str, object]] = []
        self.instances.append(self)

    def connect(self) -> None:
        self.connected = True

    def update(self, **kwargs: object) -> None:
        self.updates.append(kwargs)

    def clear(self) -> None:
        self.cleared = True

    def close(self) -> None:
        self.closed = True


class InvalidID(Exception):
    pass


class InvalidPresence(FakePresence):
    def connect(self) -> None:
        raise InvalidID("private-error-marker")


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
    capsys,
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
    stderr = capsys.readouterr().err
    assert "monitor started" in stderr
    assert "detected 2 Codex projects" in stderr
    assert "updated Discord Rich Presence" in stderr


def test_monitor_logs_detection_before_client_id_validation(
    tmp_path: Path,
    monkeypatch,
    capsys,
) -> None:
    project = tmp_path / "project"
    project.mkdir()
    monkeypatch.setattr(
        "codex_discord_rpc.cli.iter_node_repl_candidates",
        lambda: [ProjectCandidate(pid=1, started_at=10, cwd=project, identity=project)],
    )

    result = main(
        [
            "--config",
            str(tmp_path / "missing-config.toml"),
            "monitor",
            "--once",
        ]
    )

    assert result == 2
    stderr = capsys.readouterr().err
    assert "monitor started" in stderr
    assert f"detected Codex project {project.name}" in stderr
    assert str(project.parent) not in stderr
    assert "client_id is required" in stderr


def test_monitor_once_uses_idle_payload_when_desktop_is_running(
    tmp_path: Path,
    monkeypatch,
    capsys,
) -> None:
    module = types.ModuleType("pypresence")
    module.Presence = FakePresence
    monkeypatch.setitem(sys.modules, "pypresence", module)
    FakePresence.instances.clear()
    monkeypatch.setattr("codex_discord_rpc.cli.iter_node_repl_candidates", lambda: [])
    monkeypatch.setattr("codex_discord_rpc.cli.is_codex_desktop_running", lambda: True)

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
    assert instance.updates[0]["details"] == "Codex Desktopを起動中"
    assert instance.updates[0]["state"] == "待機中"
    assert "buttons" not in instance.updates[0]
    stderr = capsys.readouterr().err
    assert "Codex Desktop is running without an active project" in stderr


def test_ac018_doctor_does_not_require_discord_desktop(
    tmp_path: Path,
    monkeypatch,
    capsys,
) -> None:
    module = types.ModuleType("pypresence")
    monkeypatch.setitem(sys.modules, "pypresence", module)
    config_path = tmp_path / "config.toml"
    config_path.write_text('client_id = "123"\n', encoding="utf-8")

    result = main(["--config", str(config_path), "doctor"])

    assert result == 0
    output = capsys.readouterr().out
    assert "Discord client ID is configured" in output
    assert "Discord Desktop may be offline" in output


def test_ac015_invalid_config_returns_clean_permanent_exit(
    tmp_path: Path,
    capsys,
) -> None:
    config_path = tmp_path / "config.toml"
    config_path.write_text("refresh_interval_seconds = 1\n", encoding="utf-8")

    result = main(["--config", str(config_path), "doctor"])

    assert result == 2
    assert "configuration error: refresh_interval_seconds" in capsys.readouterr().err


def test_ac018_invalid_config_does_not_log_raw_value(
    tmp_path: Path,
    capsys,
) -> None:
    config_path = tmp_path / "config.toml"
    config_path.write_text(
        'reconnect_initial_seconds = "private-value-marker"\n',
        encoding="utf-8",
    )

    result = main(["--config", str(config_path), "doctor"])

    assert result == 2
    stderr = capsys.readouterr().err
    assert "reconnect_initial_seconds must be a number" in stderr
    assert "private-value-marker" not in stderr


def test_ac015_invalid_client_id_is_permanent_and_log_is_redacted(
    tmp_path: Path,
    monkeypatch,
    capsys,
) -> None:
    module = types.ModuleType("pypresence")
    module.Presence = InvalidPresence
    monkeypatch.setitem(sys.modules, "pypresence", module)

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

    assert result == 4
    stderr = capsys.readouterr().err
    assert "permanent Discord RPC failure (InvalidID)" in stderr
    assert "private-error-marker" not in stderr
