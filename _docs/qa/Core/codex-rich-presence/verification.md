---
title: "QA Verification: Codex Rich Presence CLI"
status: active
draft_status: n/a
qa_status: verified
risk: High
created_at: 2026-07-07
updated_at: 2026-07-10
references:
  - "_docs/intent/Core/codex-rich-presence/decision.md"
  - "_docs/archives/plan/Core/codex-rich-presence/plan.md"
  - "_docs/qa/Core/codex-rich-presence/test-plan.md"
related_issues: []
related_prs: []
---

# QA Verification: `Codex Rich Presence CLI`

## Summary

既存CLI、payload、project検出、待機中表示に加え、bounded Discord reconnect、latest desired replay、health refresh、SIGTERM clear、static doctor、checkout直結systemd user service、safe journalを実装した。fake transport、isolated installer、live Discord IPC、実user serviceで検証した。

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
uv build --out-dir <temporary-directory>
python -m compileall -q src tests
bash -n scripts/install-user-service.sh
./scripts/install-user-service.sh --dry-run
isolated XDG_CONFIG_HOME + fake systemctl --enable-now
systemd-analyze --user verify <rendered-unit>
./scripts/install-user-service.sh --enable-now
systemctl --user stop/start codex-discord-rpc.service
journalctl --user -u codex-discord-rpc.service
npx --yes markdownlint-cli2 ...
```

Result:

```text
uv sync --extra dev: installed package and dev dependencies successfully.
uv run pytest: 41 passed.
uv run ruff check .: All checks passed.
codex-discord-rpc --help: command help displayed.
codex-discord-rpc monitor --help: monitor help displayed.
codex-discord-rpc phases: Japanese phase labels displayed.
codex-discord-rpc render --repo .: Japanese payload included repo, phase, timer, and GitHub button.
codex-discord-rpc run --repo .: exited with client_id required message.
codex-discord-rpc run --repo . --client-id 123 --once: exited with clean invalid client ID error.
codex-discord-rpc monitor --once: logged detected projects and ignored stale project candidates before client ID validation.
project_detection smoke: detected live Codex node_repl project identities without reading cmdline.
./scripts/check-docs.sh: passed.
uv build: sdist and wheel built successfully.
compileall / bash syntax / systemd verify / markdownlint: passed.
isolated installer: doctor, daemon-reload, enable, restart, rendered paths passed.
live service: installed, enabled, active, Discord update acknowledged, SIGTERM clear acknowledged.
journal review: repo basename/count only; no absolute project path, raw RPC message, or credential value.
filesystem namespace probe: PrivateTmp/ProtectSystem/ProtectHome each hid cross-process /proc; omitted by intent.
```

## Automated Test Results

| Command / Test | Result | Notes |
| --- | --- | --- |
| `uv sync --extra dev` | PASS | Package builds and installs with uv. |
| `uv run pytest` | PASS | 41 tests passed. |
| `uv run ruff check .` | PASS | No lint errors. |
| `uv run codex-discord-rpc --help` | PASS | CLI entrypoint works. |
| `uv run codex-discord-rpc monitor --help` | PASS | monitor command is exposed. |
| `uv run codex-discord-rpc phases` | PASS | Japanese phase list is shown by default. |
| `uv run codex-discord-rpc render --repo .` | PASS | JSON payload was rendered without Discord Desktop. |
| `uv run codex-discord-rpc run --repo .` | PASS | Missing client ID is rejected before connection. |
| `uv run codex-discord-rpc run --repo . --client-id 123 --once` | PASS | Invalid client ID returns a clean error, not a traceback. |
| `uv run codex-discord-rpc --config /tmp/nonexistent-codex-rpc.toml monitor --once` | PASS | Detection and stale-candidate logs are emitted before client ID validation. |
| `uv run python ... project_detection` | PASS | Live `node_repl` project identities were detected from cwd/exe metadata. |
| `./scripts/check-docs.sh` | PASS | Frontmatter, TODO, links, QA, and validator fixtures passed. |
| `uv build --out-dir <tmp>` | PASS | sdist and wheel built successfully. |
| `python -m compileall -q src tests` | PASS | Python modules compiled. |
| installer dry-run / isolated enable | PASS | Checkout paths, config mode, doctor, enable and restart calls verified. |
| rendered unit + `systemd-analyze --user verify` | PASS | Unit syntax, permanent exit prevention, timeout and AF_UNIX restriction verified. |
| `systemctl --user stop/start codex-discord-rpc.service` | PASS | SIGTERM clear ACK, restart publish, enabled / active restoration. |
| live journal redaction scan | PASS | No absolute project path, raw exception, traceback, prompt, command or client ID value. |
| markdownlint selected docs | PASS | 32 Markdown files after Plan archival, 0 errors. |

## Manual QA Results

| Checklist Item | Result | Notes |
| --- | --- | --- |
| README explains project-specific usage. | PASS | Template overview was replaced with Codex Discord RPC usage. |
| README explains monitor and systemd user service usage. | PASS | monitor and user service examples are documented. |
| README explains active project TTL. | PASS | `active_project_ttl_minutes = 20` and `0` disable behavior are documented. |
| README explains idle display. | PASS | Codex Desktop open without a recent project is documented as `待機中`. |
| Quickstart explains CLI startup, render, run, and phase update. | PASS | Template adoption text was removed from the active quickstart. |
| AGENTS includes project commands and display boundaries. | PASS | Secret/privacy display restrictions are explicit. |
| TODO has no completed template tasks left. | PASS | Backlog, Ready, and In Progress are empty. |
| Static doctor | PASS | Existing config/runtime passed without treating Discord availability as a gate. |
| Live service install | PASS | Unit installed under user config, enabled, active, no systemd restarts. |
| Live project publish | PASS | Safe basename/count detection followed by Discord IPC connect and update ACK. |
| Live service stop/start | PASS | SIGTERM clear acknowledged; start reconnected and republished. |
| Filesystem hardening compatibility | PASS | Namespace-producing directives were rejected after live `/proc` detection failed; safe remaining hardening verified. |

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
| AC-010 | PASS | `tests/test_presence.py` verifies single-project and multi-project payloads include `name = "Codex (Desktop)"`. |
| AC-011 | PASS | `tests/test_project_detection.py` verifies Codex state DB recency filtering drops known stale candidates while retaining candidates without recency records. |
| AC-012 | PASS | `tests/test_cli.py` verifies fake RPC monitor sends `待機中` when Codex Desktop is running without an active project. |
| AC-013 | PASS | installer tests, dry-run, isolated enable, rendered unit and live install. |
| AC-014 | PASS | fake connect/update failures, bounded backoff, latest payload/clear replay; live initial connect/update. |
| AC-015 | PASS | clean config/InvalidID exits and unit `RestartPreventExitStatus=2 4`. |
| AC-016 | PASS | idempotent fake clear failure and live SIGTERM clear ACK/exit. |
| AC-017 | PASS | idle payload regression and configured health refresh fake-clock test. |
| AC-018 | PASS | basename/count logs, error-type-only tests and live journal redaction scan. |
| AC-019 | PASS | actual unit installed, enabled, active, publish and stop/start clear. |

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
| INV-009 | PASS | `tests/test_presence.py` asserts activity name in generated payloads. |
| INV-010 | PASS | `tests/test_project_detection.py` covers `latest_codex_project_recency_ms` and `filter_recent_projects`. |
| INV-011 | PASS | `tests/test_project_detection.py` verifies Electron-only running detection, and `tests/test_cli.py` verifies idle payload output. |
| INV-012 | PASS | transient connect/update tests and bounded backoff with latest replay. |
| INV-013 | PASS | disconnected desired state switched to clear and reconnect sent no stale update. |
| INV-014 | PASS | shutdown idempotency/clear failure test and live SIGTERM clear ACK. |
| INV-015 | PASS | idle test plus live discovery inside final user service; incompatible namespace hardening omitted. |
| INV-016 | PASS | same payload suppressed before configured interval and sent as health refresh at deadline. |
| INV-017 | PASS | CLI redaction tests, controlled config error, unit/journal scan. |
| INV-018 | PASS | offline-safe doctor and isolated/live installer preflight. |

## Deferred / Not Covered

| ID | Reason | Follow-up |
| --- | --- | --- |
| Actual Discord Desktop process restart | Avoided disrupting the active desktop session. Connect/update replay paths are deterministic fake-tested; live initial connect and service restart publish passed. | None. |
| Discord local RPC compatibility drift | `pypresence` depends on Discord's local RPC behavior. If Discord changes local IPC behavior, `render` remains usable but `run` may need adapter changes. | None for initial release. |

## Residual Risks

None

## Follow-up TODOs

None
