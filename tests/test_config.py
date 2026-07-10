from __future__ import annotations

import pytest

from codex_discord_rpc.config import Config


def test_service_runtime_defaults_are_bounded() -> None:
    config = Config.from_mapping({})

    assert config.reconnect_initial_seconds == 1.0
    assert config.reconnect_max_seconds == 30.0
    assert config.rpc_timeout_seconds == 3.0


def test_service_runtime_settings_are_configurable() -> None:
    config = Config.from_mapping(
        {
            "reconnect_initial_seconds": 2,
            "reconnect_max_seconds": 20,
            "rpc_timeout_seconds": 4,
        }
    )

    assert config.reconnect_initial_seconds == 2.0
    assert config.reconnect_max_seconds == 20.0
    assert config.rpc_timeout_seconds == 4.0


@pytest.mark.parametrize(
    "values",
    [
        {"reconnect_initial_seconds": 0},
        {"reconnect_initial_seconds": 5, "reconnect_max_seconds": 4},
        {"rpc_timeout_seconds": 0},
    ],
)
def test_invalid_service_runtime_settings_are_rejected(values: dict[str, object]) -> None:
    with pytest.raises(ValueError):
        Config.from_mapping(values)
