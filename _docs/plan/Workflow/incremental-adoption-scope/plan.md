---
title: Incremental adoption scope plan
status: active
draft_status: n/a
created_at: 2026-06-15
updated_at: 2026-06-15
references:
  - "_docs/intent/Workflow/incremental-adoption-scope/decision.md"
  - "_docs/qa/Workflow/incremental-adoption-scope/test-plan.md"
related_issues: []
related_prs: []
---

# Incremental adoption scope plan

## Overview

docs validator に opt-in のスコープ機構を追加し、既存プロジェクトへ後付け導入する際に「導入以降に追加された docs」だけを判定対象へ絞れるようにする。既定は全走査のままとし、テンプレート自身の CI 挙動は変えない。

## Scope

- 共有スコープ解決モジュール `scripts/scope.mjs` を新設する。
- `validate-frontmatter.mjs` / `validate-doc-links.mjs` / `validate-qa.mjs` の母集合走査にスコープフィルタを適用する。
- 横断チェック（リンク / references 存在、archive / qa 不変量）は起点ファイルのみ絞り、参照先存在確認は全体に対して行う。
- `docs-ci.yml` と `check-docs.sh` の該当 validator 実行に `--allow-env` と `--allow-run=git` を付与する。
- `scripts/test-validators.mjs` にスコープ機構の決定的テストを追加する。
- `_docs/standards/documentation_operations.md` に段階的導入スコープの運用節を追加する。

## Non-Goals

- `validate-todo.mjs` のスコープ化（TODO.md は常時全検証）。
- `--diff-filter=ACMR`（変更ファイルの対象化）を既定にすること。
- front-matter マーカーやディレクトリ分離方式の導入。
- テンプレート自身の CI でスコープを有効化すること（default-off を維持）。
- npm 依存の追加。

## Requirements

- **Functional**:
  - env 未設定時、3 validator の出力が変更前と同一であること。
  - `DD_SCOPE_BASE` 設定時、`git diff --name-only --diff-filter=A <ref>...HEAD` の集合のみを判定対象にすること。
  - `DD_SCOPE_PATHS` 設定時、明示リストのみを判定対象にすること（優先順位は PATHS > BASE > null）。
  - 新規 doc から既存 doc へのリンクが、既存 doc をスコープ外にしても壊れないこと。
  - `TODO.md` 検証がスコープ非依存であること。
- **Non-Functional**:
  - env / run 権限が無くても安全側（全走査）にフォールバックすること。
  - 母集合決定が `scope.mjs` に集約されていること。
  - `deno fmt --check scripts/*.mjs` を通過すること。

## Tasks

1. `scripts/scope.mjs`（`loadScope` / `makeInScope` / `normalizePath`）を実装する。
2. 3 validator の母集合走査と横断チェックにスコープを適用する。
3. CI / check-docs の実行フラグを更新する。
4. self-test にスコープ機構テストを追加する。
5. documentation_operations にスコープ運用節を追加する。
6. QA verification を作成し、`qa-review` で PASS 可否を確認する。

## QA Plan

- Risk level: Medium
- QA document: `_docs/qa/Workflow/incremental-adoption-scope/test-plan.md`
- Test strategy:
  - `scope.mjs` の決定的テスト（`DD_SCOPE_PATHS` で対象外ファイルがスキップされること）。
  - env 未設定時の出力同一性（`./scripts/check-docs.sh` 全体 PASS）。
  - git ベース経路の手動検証（`DD_SCOPE_BASE` を実 ref に設定して実行）。
  - agent misbehavior check: テンプレート本体の検証が絞られていないことの diff / 実行確認。

## Deployment / Rollout

テンプレート repo 内の scripts / docs / CI を同時更新する。外部 runtime や secret は扱わない。導入先は `DD_SCOPE_BASE` を CI に渡し、`actions/checkout` で `fetch-depth: 0` を設定するだけで段階導入できる。問題時は env を外せば全走査へ復帰する。
