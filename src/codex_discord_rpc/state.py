from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
import json
import os
import time

from .phases import normalize_phase


@dataclass(frozen=True)
class RuntimeState:
    phase: str
    started_at: int


def default_state_path() -> Path:
    state_home = os.environ.get("XDG_STATE_HOME")
    base = Path(state_home) if state_home else Path.home() / ".local" / "state"
    return base / "codex-discord-rpc" / "state.json"


def load_state(path: Path | None, fallback_phase: str, fallback_started_at: int) -> RuntimeState:
    state_path = path or default_state_path()
    if not state_path.exists():
        return RuntimeState(phase=normalize_phase(fallback_phase), started_at=fallback_started_at)

    try:
        values = json.loads(state_path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return RuntimeState(phase=normalize_phase(fallback_phase), started_at=fallback_started_at)

    phase = normalize_phase(str(values.get("phase", fallback_phase)))
    started_at = int(values.get("started_at", fallback_started_at))
    return RuntimeState(phase=phase, started_at=started_at)


def write_state(path: Path | None, phase: str, started_at: int | None = None) -> Path:
    state_path = path or default_state_path()
    state_path.parent.mkdir(parents=True, exist_ok=True)
    payload = {
        "phase": normalize_phase(phase),
        "started_at": int(started_at or time.time()),
    }
    state_path.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    return state_path
