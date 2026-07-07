---
title: "Plan: Codex Rich Presence CLI"
status: active
draft_status: n/a
created_at: 2026-07-07
updated_at: 2026-07-07
references:
  - "_docs/intent/Core/codex-rich-presence/decision.md"
  - "_docs/qa/Core/codex-rich-presence/test-plan.md"
related_issues: []
related_prs: []
---

# Plan: Codex Rich Presence CLI

## Scope

- Python / uv project packaging.
- CLI for config initialization, payload rendering, phase update, and Discord Rich Presence loop.
- Japanese display by default, optional English display by config or CLI flag.
- GitHub repository button only when a GitHub remote can be normalized.
- Unit tests for payload generation and URL normalization.

## Non-Goals

- No PR button.
- No branch, filename, prompt, command, or task text in Discord presence.
- No Codex internal hook integration in the initial version.
- No Discord bot commands.

## Implementation Steps

1. Add Python package metadata and CLI entrypoint.
2. Implement config loading and default config generation.
3. Implement phase labels and state-file based phase updates.
4. Implement git repository detection and GitHub URL normalization.
5. Implement payload rendering and Discord update loop.
6. Add tests and documentation.
7. Run unit tests, lint, CLI smoke checks, and docs validators.
