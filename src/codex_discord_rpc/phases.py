from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class PhaseLabel:
    key: str
    ja: str
    en: str


PHASES: tuple[PhaseLabel, ...] = (
    PhaseLabel("idle", "待機中", "Idle"),
    PhaseLabel("reading_context", "文脈を確認中", "Reading context"),
    PhaseLabel("editing", "編集中", "Editing"),
    PhaseLabel("running_commands", "コマンド実行中", "Running commands"),
    PhaseLabel("running_tests", "テスト実行中", "Running tests"),
    PhaseLabel("reviewing_changes", "変更を確認中", "Reviewing changes"),
    PhaseLabel("waiting_for_input", "入力待ち", "Waiting for input"),
)

_PHASE_BY_KEY = {phase.key: phase for phase in PHASES}


def normalize_phase(value: str | None) -> str:
    if not value:
        return "editing"
    normalized = value.strip().lower().replace("-", "_").replace(" ", "_")
    if normalized not in _PHASE_BY_KEY:
        valid = ", ".join(sorted(_PHASE_BY_KEY))
        raise ValueError(f"unknown phase: {value!r}; valid phases: {valid}")
    return normalized


def phase_label(phase: str, language: str) -> str:
    item = _PHASE_BY_KEY[normalize_phase(phase)]
    return item.en if language == "en" else item.ja


def phase_table(language: str) -> list[tuple[str, str]]:
    return [(phase.key, phase.en if language == "en" else phase.ja) for phase in PHASES]
