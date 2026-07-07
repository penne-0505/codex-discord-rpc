from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
import re
import subprocess


@dataclass(frozen=True)
class RepositoryInfo:
    root: Path
    name: str
    github_url: str | None


def _git(repo_path: Path, *args: str) -> str | None:
    try:
        result = subprocess.run(
            ["git", *args],
            cwd=repo_path,
            check=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.DEVNULL,
            text=True,
        )
    except (FileNotFoundError, subprocess.CalledProcessError):
        return None
    output = result.stdout.strip()
    return output or None


def normalize_github_remote(remote: str | None) -> str | None:
    if not remote:
        return None
    remote = remote.strip()

    # intent: INV-002 (Core/codex-rich-presence) — Only recognized GitHub remotes create public buttons.
    ssh_match = re.fullmatch(r"git@github\.com:([^/\s]+)/([^/\s]+?)(?:\.git)?", remote)
    if ssh_match:
        owner, repo = ssh_match.groups()
        return f"https://github.com/{owner}/{repo}"

    https_match = re.fullmatch(r"https://github\.com/([^/\s]+)/([^/\s]+?)(?:\.git)?/?", remote)
    if https_match:
        owner, repo = https_match.groups()
        return f"https://github.com/{owner}/{repo}"

    return None


def get_repository_info(repo_path: str | Path) -> RepositoryInfo:
    path = Path(repo_path).expanduser().resolve()
    root_output = _git(path, "rev-parse", "--show-toplevel")
    root = Path(root_output).resolve() if root_output else path
    name = root.name
    remote = _git(root, "remote", "get-url", "origin")
    return RepositoryInfo(root=root, name=name, github_url=normalize_github_remote(remote))
