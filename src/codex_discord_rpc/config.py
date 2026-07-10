from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
import os
import tomllib

from .phases import normalize_phase


def _integer(values: dict[str, object], key: str, default: int) -> int:
    try:
        return int(values.get(key, default))
    except (TypeError, ValueError):
        raise ValueError(f"{key} must be an integer") from None


def _number(values: dict[str, object], key: str, default: float) -> float:
    try:
        return float(values.get(key, default))
    except (TypeError, ValueError):
        raise ValueError(f"{key} must be a number") from None


DEFAULT_CONFIG = """# Codex Discord Rich Presence configuration
enabled = true
language = "ja"
client_id = ""
show_repository_button = true
show_timer = true
large_image_key = ""
auto_detect_projects = true
active_project_ttl_minutes = 20
repo_path = "."
phase = "editing"
refresh_interval_seconds = 15
reconnect_initial_seconds = 1
reconnect_max_seconds = 30
rpc_timeout_seconds = 3
state_file = ""
"""


@dataclass(frozen=True)
class Config:
    enabled: bool = True
    language: str = "ja"
    client_id: str = ""
    show_repository_button: bool = True
    show_timer: bool = True
    large_image_key: str = ""
    auto_detect_projects: bool = True
    active_project_ttl_minutes: int = 20
    repo_path: str = "."
    phase: str = "editing"
    refresh_interval_seconds: int = 15
    reconnect_initial_seconds: float = 1.0
    reconnect_max_seconds: float = 30.0
    rpc_timeout_seconds: float = 3.0
    state_file: str = ""

    @classmethod
    def from_mapping(cls, values: dict[str, object]) -> "Config":
        language = str(values.get("language", "ja")).strip().lower()
        if language not in {"ja", "en"}:
            raise ValueError("language must be 'ja' or 'en'")

        interval = _integer(values, "refresh_interval_seconds", 15)
        if interval < 5:
            raise ValueError("refresh_interval_seconds must be 5 or greater")

        reconnect_initial = _number(values, "reconnect_initial_seconds", 1)
        reconnect_max = _number(values, "reconnect_max_seconds", 30)
        rpc_timeout = _number(values, "rpc_timeout_seconds", 3)
        if reconnect_initial <= 0:
            raise ValueError("reconnect_initial_seconds must be positive")
        if reconnect_max < reconnect_initial:
            raise ValueError("reconnect_max_seconds must not be less than reconnect_initial_seconds")
        if rpc_timeout <= 0:
            raise ValueError("rpc_timeout_seconds must be positive")

        ttl_minutes = _integer(values, "active_project_ttl_minutes", 20)
        if ttl_minutes < 0:
            raise ValueError("active_project_ttl_minutes must be 0 or greater")

        return cls(
            enabled=bool(values.get("enabled", True)),
            language=language,
            client_id=str(values.get("client_id", "")).strip(),
            show_repository_button=bool(values.get("show_repository_button", True)),
            show_timer=bool(values.get("show_timer", True)),
            large_image_key=str(values.get("large_image_key", "")).strip(),
            auto_detect_projects=bool(values.get("auto_detect_projects", True)),
            active_project_ttl_minutes=ttl_minutes,
            repo_path=str(values.get("repo_path", ".")),
            phase=normalize_phase(str(values.get("phase", "editing"))),
            refresh_interval_seconds=interval,
            reconnect_initial_seconds=reconnect_initial,
            reconnect_max_seconds=reconnect_max,
            rpc_timeout_seconds=rpc_timeout,
            state_file=str(values.get("state_file", "")),
        )


def default_config_path() -> Path:
    config_home = os.environ.get("XDG_CONFIG_HOME")
    base = Path(config_home) if config_home else Path.home() / ".config"
    return base / "codex-discord-rpc" / "config.toml"


def load_config(path: Path | None = None) -> Config:
    config_path = path or default_config_path()
    if not config_path.exists():
        return Config()
    with config_path.open("rb") as handle:
        return Config.from_mapping(tomllib.load(handle))


def write_default_config(path: Path | None = None, overwrite: bool = False) -> Path:
    config_path = path or default_config_path()
    if config_path.exists() and not overwrite:
        raise FileExistsError(f"config already exists: {config_path}")
    config_path.parent.mkdir(parents=True, exist_ok=True)
    config_path.write_text(DEFAULT_CONFIG, encoding="utf-8")
    return config_path
