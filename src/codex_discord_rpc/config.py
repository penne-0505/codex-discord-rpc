from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
import os
import tomllib

from .phases import normalize_phase


DEFAULT_CONFIG = """# Codex Discord Rich Presence configuration
enabled = true
language = "ja"
client_id = ""
show_repository_button = true
show_timer = true
auto_detect_projects = true
repo_path = "."
phase = "editing"
refresh_interval_seconds = 15
state_file = ""
"""


@dataclass(frozen=True)
class Config:
    enabled: bool = True
    language: str = "ja"
    client_id: str = ""
    show_repository_button: bool = True
    show_timer: bool = True
    auto_detect_projects: bool = True
    repo_path: str = "."
    phase: str = "editing"
    refresh_interval_seconds: int = 15
    state_file: str = ""

    @classmethod
    def from_mapping(cls, values: dict[str, object]) -> "Config":
        language = str(values.get("language", "ja")).strip().lower()
        if language not in {"ja", "en"}:
            raise ValueError("language must be 'ja' or 'en'")

        interval = int(values.get("refresh_interval_seconds", 15))
        if interval < 5:
            raise ValueError("refresh_interval_seconds must be 5 or greater")

        return cls(
            enabled=bool(values.get("enabled", True)),
            language=language,
            client_id=str(values.get("client_id", "")).strip(),
            show_repository_button=bool(values.get("show_repository_button", True)),
            show_timer=bool(values.get("show_timer", True)),
            auto_detect_projects=bool(values.get("auto_detect_projects", True)),
            repo_path=str(values.get("repo_path", ".")),
            phase=normalize_phase(str(values.get("phase", "editing"))),
            refresh_interval_seconds=interval,
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
