from pathlib import Path

from codex_discord_rpc.config import Config
from codex_discord_rpc.git_info import RepositoryInfo
from codex_discord_rpc.presence import build_multi_project_payload, build_payload


def test_builds_japanese_repo_phase_timer_payload() -> None:
    config = Config(language="ja", show_timer=True, show_repository_button=True)
    repo = RepositoryInfo(
        root=Path("/tmp/codex-discord-rpc"),
        name="codex-discord-rpc",
        github_url="https://github.com/penne-0505/codex-discord-rpc",
    )

    payload = build_payload(config, repo, "editing", started_at=1_700_000_000).as_rpc_kwargs()

    assert payload["details"] == "codex-discord-rpc で作業中"
    assert payload["state"] == "編集中"
    assert payload["start"] == 1_700_000_000
    assert payload["buttons"] == [
        {
            "label": "リポジトリを見る",
            "url": "https://github.com/penne-0505/codex-discord-rpc",
        }
    ]
    assert "large_image" not in payload


def test_includes_large_image_when_configured() -> None:
    config = Config(language="ja", large_image_key="codex_icon")
    repo = RepositoryInfo(
        root=Path("/tmp/codex-discord-rpc"),
        name="codex-discord-rpc",
        github_url=None,
    )

    payload = build_payload(config, repo, "editing", started_at=1).as_rpc_kwargs()

    assert payload["large_image"] == "codex_icon"


def test_omits_repository_button_when_url_is_unavailable() -> None:
    config = Config(language="ja", show_repository_button=True)
    repo = RepositoryInfo(root=Path("/tmp/local"), name="local", github_url=None)

    payload = build_payload(config, repo, "running_tests", started_at=1).as_rpc_kwargs()

    assert payload["state"] == "テスト実行中"
    assert "buttons" not in payload


def test_supports_english_labels_by_config() -> None:
    config = Config(language="en")
    repo = RepositoryInfo(root=Path("/tmp/koto"), name="koto", github_url=None)

    payload = build_payload(config, repo, "waiting_for_input", started_at=1).as_rpc_kwargs()

    assert payload["details"] == "Working on koto"
    assert payload["state"] == "Waiting for input"


def test_builds_japanese_multi_project_payload_without_buttons() -> None:
    config = Config(
        language="ja",
        show_timer=True,
        show_repository_button=True,
        large_image_key="codex_icon",
    )

    payload = build_multi_project_payload(config, 3, started_at=1_700_000_000).as_rpc_kwargs()

    assert payload["details"] == "3個のCodexプロジェクトで作業中"
    assert payload["state"] == "複数プロジェクト"
    assert payload["start"] == 1_700_000_000
    assert payload["large_image"] == "codex_icon"
    assert "buttons" not in payload
