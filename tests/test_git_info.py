from codex_discord_rpc.git_info import normalize_github_remote


def test_normalize_github_https_remote() -> None:
    assert (
        normalize_github_remote("https://github.com/penne-0505/codex-discord-rpc.git")
        == "https://github.com/penne-0505/codex-discord-rpc"
    )


def test_normalize_github_ssh_remote() -> None:
    assert (
        normalize_github_remote("git@github.com:penne-0505/codex-discord-rpc.git")
        == "https://github.com/penne-0505/codex-discord-rpc"
    )


def test_non_github_remote_has_no_button_url() -> None:
    assert normalize_github_remote("https://example.com/owner/repo.git") is None
