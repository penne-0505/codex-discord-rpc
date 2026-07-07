from __future__ import annotations

from pathlib import Path
import sys
import types

from codex_discord_rpc.cli import main


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
