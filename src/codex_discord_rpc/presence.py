from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
import time
from typing import Any

from .config import Config
from .git_info import RepositoryInfo, get_repository_info
from .phases import phase_label
from .state import load_state


APPLICATION_LABEL = "Codex (Desktop)"


@dataclass(frozen=True)
class PresencePayload:
    name: str
    details: str
    state: str
    start: int | None
    buttons: list[dict[str, str]] | None
    large_text: str
    large_image: str | None

    def as_rpc_kwargs(self) -> dict[str, Any]:
        payload: dict[str, Any] = {
            "name": self.name,
            "details": self.details,
            "state": self.state,
            "large_text": self.large_text,
        }
        if self.large_image:
            payload["large_image"] = self.large_image
        if self.start is not None:
            payload["start"] = self.start
        if self.buttons:
            payload["buttons"] = self.buttons
        return payload


def build_payload(
    config: Config,
    repository: RepositoryInfo,
    phase: str,
    started_at: int | None = None,
) -> PresencePayload:
    details = (
        f"{repository.name} で作業中"
        if config.language == "ja"
        else f"Working on {repository.name}"
    )
    label = "リポジトリを見る" if config.language == "ja" else "View Repository"
    buttons = (
        [{"label": label, "url": repository.github_url}]
        if config.show_repository_button and repository.github_url
        else None
    )
    return PresencePayload(
        name=APPLICATION_LABEL,
        details=details,
        state=phase_label(phase, config.language),
        start=int(started_at or time.time()) if config.show_timer else None,
        buttons=buttons,
        large_text=APPLICATION_LABEL,
        large_image=config.large_image_key or None,
    )


def build_multi_project_payload(
    config: Config,
    project_count: int,
    started_at: int | None = None,
) -> PresencePayload:
    details = (
        f"{project_count}個のCodexプロジェクトで作業中"
        if config.language == "ja"
        else f"Working in {project_count} Codex projects"
    )
    state = "複数プロジェクト" if config.language == "ja" else "Multiple projects"
    return PresencePayload(
        name=APPLICATION_LABEL,
        details=details,
        state=state,
        start=int(started_at or time.time()) if config.show_timer else None,
        buttons=None,
        large_text=APPLICATION_LABEL,
        large_image=config.large_image_key or None,
    )


def render_payload(config: Config, repo_path: str | Path | None = None) -> PresencePayload:
    started_at = int(time.time())
    state_path = Path(config.state_file).expanduser() if config.state_file else None
    runtime_state = load_state(state_path, config.phase, started_at)
    repository = get_repository_info(repo_path or config.repo_path)
    return build_payload(config, repository, runtime_state.phase, runtime_state.started_at)
