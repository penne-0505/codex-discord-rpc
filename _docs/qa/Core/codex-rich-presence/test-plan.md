---
title: "QA Test Plan: Codex Rich Presence CLI"
status: active
draft_status: n/a
qa_status: planned
risk: Medium
created_at: 2026-07-07
updated_at: 2026-07-07
references:
  - "_docs/intent/Core/codex-rich-presence/decision.md"
  - "_docs/plan/Core/codex-rich-presence/plan.md"
related_issues: []
related_prs: []
---

# QA Test Plan: `Codex Rich Presence CLI`

## Source of Intent

- TODO: `Core-Feat-9`
- Plan: `_docs/plan/Core/codex-rich-presence/plan.md`
- Intent: `_docs/intent/Core/codex-rich-presence/decision.md`

## Quality Goal

Discordへ出す情報をrepo名、作業フェーズ、timerに絞り、GitHub URLボタンは安全に正規化できる場合だけ生成されることを確認する。

## Acceptance Criteria

- AC-001: Python / uv projectとしてinstallでき、`codex-discord-rpc` CLIが使える。
- AC-002: `render` が日本語のrepo + phase + timer payloadをJSONで出力する。
- AC-003: `run` は設定されたDiscord client IDでRich Presence更新を試みる。
- AC-004: GitHub remote URLが正規化できる場合だけ `リポジトリを見る` ボタンを生成する。
- AC-005: README / Quickstart / AGENTS がプロジェクト固有の利用方法を説明している。

## Intent-derived Invariants

- INV-001: Rich Presence payloadはrepo名、phase、timer、正規化済みGitHub URLボタン以外の作業詳細を含まない。
- INV-002: GitHubボタンは `git@github.com:owner/repo(.git)` または `https://github.com/owner/repo(.git)` から正規化できる場合だけ生成される。
- INV-003: 日本語表示がデフォルトであり、英語表示は明示設定時だけ使われる。
- INV-004: Discord接続なしでpayload生成を検証できるCLIとテストが存在する。

## Risk Assessment

- Risk level: Medium
- Risk rationale: Discord RPC連携と公開表示内容を扱うため、表示漏れと誤表示の検証が必要。
- Regression risk: phaseやpayload schemaの変更で表示粒度が崩れる可能性がある。
- Data safety risk: 永続化するのはphaseと開始時刻だけ。
- Security / privacy risk: ファイル名、branch名、プロンプト本文、コマンド内容を表示しないことで抑制する。
- UX risk: Discord Desktop未起動時は `run` が失敗するため、`render` で事前確認できるようにする。
- Agent misbehavior risk: template由来TODOやREADMEを残すと完成済みrepoと誤認しにくくなるため、docsをプロジェクト固有化する。

## Test Strategy

- Unit: URL正規化、payload生成、言語切り替えをpytestで確認する。
- Integration: `uv run codex-discord-rpc render --repo .` を実行する。
- E2E: Discord Desktop接続はローカル環境依存のため、client ID未設定時の安全な失敗のみ確認する。
- Manual QA: README/Quickstart/AGENTS/TODOの内容を確認する。
- Validator / static check: `uv run ruff check .` と `./scripts/check-docs.sh` を実行する。
- Diff review: secretや作業詳細を出すフィールドがないことを確認する。

## Test Matrix

| ID | Source | Requirement / Invariant | Test Type | Command / File | Expected Evidence | Status |
| --- | --- | --- | --- | --- | --- | --- |
| AC-001 | TODO | Python / uv projectとしてCLIが使える | integration | `uv run codex-discord-rpc --help` | CLI helpが表示される | planned |
| AC-002 | TODO | 日本語payloadをJSONで出力する | integration | `uv run codex-discord-rpc render --repo .` | `で作業中` と日本語phaseを含むJSON | planned |
| AC-003 | TODO | `run` がclient ID必須で動作する | integration | `uv run codex-discord-rpc run --repo .` | client ID未設定では明示エラー | planned |
| AC-004 | TODO | GitHub URLのときだけボタン生成 | unit | `uv run pytest` | URL正規化テストが通る | planned |
| AC-005 | TODO | docsがプロジェクト固有化される | manual | README/Quickstart/AGENTS/TODO review | テンプレート初期案内が運用入口に残らない | planned |
| INV-001 | intent | payloadに作業詳細を含めない | unit/review | `tests/test_presence.py`, diff review | details/state/start/buttonsのみ | planned |
| INV-002 | intent | GitHub remoteだけボタン化する | unit | `tests/test_git_info.py` | non-GitHub remoteはNone | planned |
| INV-003 | intent | 日本語デフォルト、英語は明示時のみ | unit | `tests/test_presence.py` | ja/enの期待値が通る | planned |
| INV-004 | intent | Discord接続なしでpayload検証可能 | integration | `uv run codex-discord-rpc render --repo .` | DiscordなしでJSON出力 | planned |

## Manual QA Checklist

- [ ] READMEがCodex Discord RPCの目的と利用手順を説明している。
- [ ] Quickstartがテンプレート初期作業ではなく、このCLIの起動手順を説明している。
- [ ] AGENTSがプロジェクト固有コマンドと表示境界を説明している。
- [ ] TODOに完了済みテンプレート作業や不要な導入スコープ作業が残っていない。

## Regression Checklist

- [ ] 日本語phase labelが維持されている。
- [ ] GitHub以外のremoteからボタンを作らない。
- [ ] renderはDiscord Desktopなしで動く。

## High-risk Checklist

Use this section only for Risk High / Critical.

- [ ] Not applicable.

## Out of Scope

- PRボタン。
- branch名、ファイル名、プロンプト本文、コマンド内容の表示。
- Codex内部hookとの自動統合。

## Open Questions

- None.
