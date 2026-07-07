---
title: "QA Verification: Codex Rich Presence CLI"
status: active
draft_status: n/a
qa_status: verified
risk: Medium
created_at: 2026-07-07
updated_at: 2026-07-07
references:
  - "_docs/intent/Core/codex-rich-presence/decision.md"
  - "_docs/plan/Core/codex-rich-presence/plan.md"
  - "_docs/qa/Core/codex-rich-presence/test-plan.md"
related_issues: []
related_prs: []
---

# QA Verification: `Codex Rich Presence CLI`

## Summary

Python / uv CLI、payload生成、GitHub URL正規化、日本語表示、large image key設定、fake RPCによるRich Presence更新経路、Linux `node_repl` cwd project検出、複数project aggregate表示、monitor状態変化ログ、invalid client ID時の安全な失敗、docs validatorを確認した。

## Verification Verdict

Verdict: PASS

## Commands Run

```bash
uv sync --extra dev
uv run pytest
uv run ruff check .
uv run codex-discord-rpc --help
uv run codex-discord-rpc monitor --help
uv run codex-discord-rpc phases
uv run codex-discord-rpc render --repo .
uv run codex-discord-rpc run --repo .
uv run codex-discord-rpc run --repo . --client-id 123 --once
uv run codex-discord-rpc --config /tmp/nonexistent-codex-rpc.toml monitor --once
uv run python - <<'PY'
from codex_discord_rpc.project_detection import distinct_projects, iter_node_repl_candidates
for c in distinct_projects(iter_node_repl_candidates())[:10]:
    print(c.pid, c.started_at, c.identity)
PY
./scripts/check-docs.sh
```

Result:

```text
uv sync --extra dev: installed package and dev dependencies successfully.
uv run pytest: 15 passed.
uv run ruff check .: All checks passed.
codex-discord-rpc --help: command help displayed.
codex-discord-rpc monitor --help: monitor help displayed.
codex-discord-rpc phases: Japanese phase labels displayed.
codex-discord-rpc render --repo .: Japanese payload included repo, phase, timer, and GitHub button.
codex-discord-rpc run --repo .: exited with client_id required message.
codex-discord-rpc run --repo . --client-id 123 --once: exited with clean invalid client ID error.
codex-discord-rpc monitor --once: logged detected projects before client ID validation.
project_detection smoke: detected live Codex node_repl project identities without reading cmdline.
./scripts/check-docs.sh: passed.
```

## Automated Test Results

| Command / Test | Result | Notes |
| --- | --- | --- |
| `uv sync --extra dev` | PASS | Package builds and installs with uv. |
| `uv run pytest` | PASS | 15 tests passed. |
| `uv run ruff check .` | PASS | No lint errors. |
| `uv run codex-discord-rpc --help` | PASS | CLI entrypoint works. |
| `uv run codex-discord-rpc monitor --help` | PASS | monitor command is exposed. |
| `uv run codex-discord-rpc phases` | PASS | Japanese phase list is shown by default. |
| `uv run codex-discord-rpc render --repo .` | PASS | JSON payload was rendered without Discord Desktop. |
| `uv run codex-discord-rpc run --repo .` | PASS | Missing client ID is rejected before connection. |
| `uv run codex-discord-rpc run --repo . --client-id 123 --once` | PASS | Invalid client ID returns a clean error, not a traceback. |
| `uv run codex-discord-rpc --config /tmp/nonexistent-codex-rpc.toml monitor --once` | PASS | Detection logs are emitted before client ID validation. |
| `uv run python ... project_detection` | PASS | Live `node_repl` project identities were detected from cwd/exe metadata. |
| `./scripts/check-docs.sh` | PASS | Frontmatter, TODO, links, QA, and validator fixtures passed. |

## Manual QA Results

| Checklist Item | Result | Notes |
| --- | --- | --- |
| README explains project-specific usage. | PASS | Template overview was replaced with Codex Discord RPC usage. |
| README explains monitor and systemd user service usage. | PASS | monitor and user service examples are documented. |
| Quickstart explains CLI startup, render, run, and phase update. | PASS | Template adoption text was removed from the active quickstart. |
| AGENTS includes project commands and display boundaries. | PASS | Secret/privacy display restrictions are explicit. |
| TODO has no completed template tasks left. | PASS | Backlog, Ready, and In Progress are empty. |

## Acceptance Criteria Coverage

| ID | Result | Evidence |
| --- | --- | --- |
| AC-001 | PASS | `uv sync --extra dev` and `uv run codex-discord-rpc --help` succeeded. |
| AC-002 | PASS | `render --repo .` emitted `codex-discord-rpc で作業中`, `編集中`, `start`, and a GitHub button. |
| AC-003 | PASS | `tests/test_cli.py` verifies `run --once` updates a fake RPC; CLI rejects missing or invalid client ID cleanly. |
| AC-004 | PASS | `tests/test_git_info.py` covers HTTPS, SSH, and non-GitHub remotes. |
| AC-005 | PASS | README, Quickstart, and AGENTS were reviewed after customization. |
| AC-006 | PASS | `tests/test_project_detection.py` verifies fake `/proc` `node_repl` cwd detection. |
| AC-007 | PASS | `tests/test_cli.py` and `tests/test_presence.py` verify aggregate multi-project payload with no buttons. |
| AC-008 | PASS | `tests/test_presence.py` verifies `large_image` is omitted by default and included when `large_image_key` is configured. |
| AC-009 | PASS | `tests/test_cli.py` verifies monitor stderr includes startup, detection, update logs, and pre-client-ID detection logs. |

## Invariant Coverage

| ID | Result | Evidence |
| --- | --- | --- |
| INV-001 | PASS | `tests/test_presence.py` asserts payload fields and no file/branch/task fields exist. |
| INV-002 | PASS | `tests/test_git_info.py` allows only recognized GitHub remotes. |
| INV-003 | PASS | `tests/test_presence.py` covers default Japanese and explicit English labels. |
| INV-004 | PASS | `render --repo .` works without Discord Desktop, and pytest covers payload generation. |
| INV-005 | PASS | `tests/test_project_detection.py`, `tests/test_cli.py`, and `tests/test_presence.py` cover project detection and multi-project aggregate display. |
| INV-006 | PASS | Diff review confirms `project_detection.py` reads `/proc/*/exe` and `/proc/*/cwd`, not `/proc/*/cmdline`. |
| INV-007 | PASS | `tests/test_presence.py` covers default omission and configured `large_image` output. |
| INV-008 | PASS | `tests/test_cli.py` asserts monitor status logs for the multi-project path and missing-client-ID path. |

## Deferred / Not Covered

| ID | Reason | Follow-up |
| --- | --- | --- |
| Live Discord profile visual confirmation | Requires a real Discord application client ID and running Discord Desktop session. Core update path is covered by fake RPC and invalid-ID smoke. | None for initial release. |
| Discord local RPC compatibility drift | `pypresence` depends on Discord's local RPC behavior. If Discord changes local IPC behavior, `render` remains usable but `run` may need adapter changes. | None for initial release. |

## Residual Risks

None

## Follow-up TODOs

- None.
