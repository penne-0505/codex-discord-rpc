---
title: "Plan: Codex Rich Presence CLI"
status: archived
draft_status: n/a
created_at: 2026-07-07
updated_at: 2026-07-10
references:
  - "_docs/intent/Core/codex-rich-presence/decision.md"
  - "_docs/qa/Core/codex-rich-presence/test-plan.md"
related_issues: []
related_prs: []
---

# Plan: Codex Rich Presence CLI

## Overview

Codex Desktopのproject状態をDiscord Rich Presenceへ共有するCLIを、checkout直結のsystemd user serviceとして
常駐運用できる状態へ拡張する。通常のDiscord未起動・再起動はmonitor内部で回復し、systemdはprocess failureの
監督とlogin時起動を担当する。

## Scope

- Python / uv project packaging.
- CLI for config initialization, payload rendering, phase update, and Discord Rich Presence loop.
- Japanese display by default, optional English display by config or CLI flag.
- GitHub repository button only when a GitHub remote can be normalized.
- Linux monitor mode that detects Codex Desktop project directories from `node_repl` process cwd values.
- Aggregate multi-project display when multiple distinct Codex project roots are detected.
- Unit tests for payload generation and URL normalization.
- Bounded Discord reconnect、latest desired replay、SIGTERM cleanupを持つmonitor runtime。
- Checkout-local `.venv`を使うsystemd user unit template、installer、static doctor。
- Codex Desktop起動中・active projectなしの待機中表示を常駐serviceでも維持する。

## Non-Goals

- No PR button.
- No branch, filename, prompt, command, or task text in Discord presence.
- No Codex internal hook integration in the initial version.
- No Discord bot commands.
- No foreground-window or active-thread detection. Multiple detected projects are intentionally shown as an aggregate.
- No direct Discord IPC rewrite; `pypresence`の同期updateを低頻度health probeとして利用する。
- No self-update or automatic `.venv` recreation. Checkout移動後はinstallerを再実行する。
- No system-wide service; current Linux userのgraphical sessionだけを対象にする。

## Requirements

- Discord接続前後のtransient failureをbounded exponential backoffし、processを終了しない。
- invalid client ID、missing config/dependencyはpermanent failureとしてclean exitする。
- reconnect後は最後に計算したdesired payloadまたはclearだけを即時replayする。
- pypresenceがbackground pipe readerを持たないため、configured refresh intervalのupdateをhealth probeとして残す。
- SIGINT / SIGTERMはinterruptible waitを解除し、best-effort clear、close、exit 0を行う。
- service journalはprojectのbasename/countとerror typeだけを記録し、absolute pathやraw exception messageを残さない。
- installerは`--dry-run`、`--enable-now`、`--disable-now`を持ち、Discordを起動条件にしないstatic doctorを通す。
- unitはgraphical sessionに連動し、checkoutの`.venv/bin/codex-discord-rpc`とuser configを絶対pathで参照する。
- unitは`NoNewPrivileges`とAF_UNIX限定を使う。filesystem namespace hardeningは他desktop processの`/proc`検出を壊すため使わない。

## Implementation Steps

1. Add Python package metadata and CLI entrypoint.
2. Implement config loading and default config generation.
3. Implement phase labels and state-file based phase updates.
4. Implement git repository detection and GitHub URL normalization.
5. Implement payload rendering and Discord update loop.
6. Implement monitor mode and project aggregation.
7. Add tests and documentation.
8. Run unit tests, lint, CLI smoke checks, and docs validators.
9. Extract a deterministic Presence reconnect coordinator with fake-clock tests.
10. Add monitor signal lifecycle, permanent/transient error classification, and safe journal logging.
11. Add doctor, config example, systemd unit template, and checkout-bound installer.
12. Install and enable the live user service; verify publish, stop clear, restart, and disabled rollback.
13. Update verification and archive this Plan after the completion checklist passes.

## QA Plan

- QA document: `_docs/qa/Core/codex-rich-presence/test-plan.md`
- Risk: High。external Discord IPC、login時常駐、systemd lifecycleを扱う。
- Unit: backoff、latest-only replay、clear desired、health refresh、permanent error、shutdown idempotency。
- Integration: doctor、installer dry-run、rendered unit、systemd verify、isolated config home。
- Live: current Discordへのpublish、service stop clear、enable/start、journal redaction。
- Rollback: `--disable-now`でunitを停止・無効化し、configとunitは調査用に保持する。

## Deployment / Rollout

1. Fake RPCとtemporary user pathsでruntime / installerを検証する。
2. Existing user configをstatic doctorで確認する。Discordの起動有無はgateにしない。
3. Checkout絶対pathを埋め込んだunitをinstallし、`enable --now`する。
4. Live publishとSIGTERM clearを確認後、serviceをenabled / activeへ戻す。
5. 問題時は`--disable-now`でrollbackする。checkout移動・`.venv`再作成後はinstallerを再実行する。
