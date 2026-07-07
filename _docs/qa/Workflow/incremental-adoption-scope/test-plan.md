---
title: "QA Test Plan: Incremental adoption scope"
status: active
draft_status: n/a
qa_status: planned
risk: Medium
created_at: 2026-06-15
updated_at: 2026-06-15
references:
  - "_docs/intent/Workflow/incremental-adoption-scope/decision.md"
  - "_docs/plan/Workflow/incremental-adoption-scope/plan.md"
related_issues: []
related_prs: []
---

# QA Test Plan: `Incremental adoption scope`

## Source of Intent

- TODO: `Workflow-Feat-6`
- Plan: `_docs/plan/Workflow/incremental-adoption-scope/plan.md`
- Intent: `_docs/intent/Workflow/incremental-adoption-scope/decision.md`

## Quality Goal

既存プロジェクトへ後付け導入する際、既存 docs に手を入れずに「導入以降に追加された docs」だけを品質ゲートへ載せられること。同時に、テンプレート自身の全走査検証（dogfooding）を一切弱めないこと。

## Acceptance Criteria

- AC-001: `DD_SCOPE_BASE` / `DD_SCOPE_PATHS` が未設定のとき、`validate-frontmatter` / `validate-doc-links` / `validate-qa` の判定結果が変更前と同一（全走査）である。
- AC-002: `DD_SCOPE_PATHS` に対象外パスのみを指定すると、対象外の不正 doc が判定されず exit 0 になる。
- AC-003: `DD_SCOPE_PATHS` に不正 doc を含めると、従来通り error で exit 非 0 になる。
- AC-004: スコープの母集合決定が `scripts/scope.mjs` に集約され、3 validator がそれを共有する。
- AC-005: `validate-todo.mjs` の検証はスコープ設定の有無に関わらず `TODO.md` 全体を対象とする。
- AC-006: `_docs/standards/documentation_operations.md` に `DD_SCOPE_BASE` の使い方・`fetch-depth`・必要権限・`--diff-filter=A` の意味・TODO 常時検証が記載される。

## Intent-derived Invariants

- INV-001: `DD_SCOPE_BASE` と `DD_SCOPE_PATHS` が未設定のとき、各 validator は従来通り全 docs を走査する。
- INV-002: スコープ有効時、判定対象は追加されたファイル（`--diff-filter=A` 相当）のみで、既存ファイルは判定されない。
- INV-003: 横断的整合チェックは起点ファイルをスコープで絞っても、参照先の存在確認はファイルシステム全体に対して行う。
- INV-004: `TODO.md` の検証はスコープ設定の有無に関わらず全タスクを対象とする。
- INV-005: スコープの母集合決定は `scripts/scope.mjs` に集約され、frontmatter / doc-links / qa validator がそれを共有する。
- INV-006: env / run 権限が無い場合、スコープ解決は scope = null（全走査）へフォールバックする。

## Risk Assessment

- Risk level: Medium
- Risk rationale: validator / CI のファイル選定ロジックを横断的に変更する。失敗時の影響は品質ゲートの判定範囲。
- Regression risk: env 未設定時に従来の全走査挙動が変わると、テンプレート自身の検証が弱まる / 過剰になる。
- Data safety risk: None（読み取りのみ。破壊的操作なし）。
- Security / privacy risk: Low（`--allow-env` と `--allow-run=git` を追加するが、git 読み取りに限定）。
- UX risk: None（contributor / CI ワークフロー向け）。
- Agent misbehavior risk: agent が「スコープ = 検証を弱める」と誤解し、テンプレート本体の検証まで絞る / TODO 検証をスコープ化する / フォールバックを under-checking 側へ倒す可能性。

## Test Strategy

- Unit: `scope.mjs` の挙動を `DD_SCOPE_PATHS` 経由で決定的に検証（self-test に追加）。
- Integration: `./scripts/check-docs.sh` 全体を env 未設定で実行し、従来通り PASS することを確認。
- Manual QA: `DD_SCOPE_BASE` を実 git ref に設定して validator を実行し、スコープ集合が期待通り絞られることを確認。
- Validator / static check: `deno fmt --check scripts/*.mjs`、各 validator 個別実行。
- Diff review: 母集合決定が `scope.mjs` に集約されたこと、`validate-todo.mjs` が非スコープのままであることを確認。

## Test Matrix

| ID | Source | Requirement / Invariant | Test Type | Command / File | Expected Evidence | Status |
| --- | --- | --- | --- | --- | --- | --- |
| AC-001 | TODO | env 未設定時に全走査挙動が同一。 | validator | `./scripts/check-docs.sh` | env なしで exit 0、従来通り全 docs を検証。 | planned |
| AC-002 | TODO | 対象外パス指定で不正 doc がスキップされる。 | self-test | `scripts/test-validators.mjs` | `DD_SCOPE_PATHS` が除外した invalid fixture で exit 0。 | planned |
| AC-003 | TODO | 対象内に不正 doc を含めると従来通り失敗。 | self-test | `scripts/test-validators.mjs` | `DD_SCOPE_PATHS` が含める invalid fixture で exit 非 0。 | planned |
| AC-004 | TODO | 母集合決定が scope.mjs に集約。 | diff review | `scripts/scope.mjs`, `scripts/validate-*.mjs` | 3 validator が `loadScope` / `makeInScope` を import。 | planned |
| AC-005 | TODO | TODO 検証はスコープ非依存。 | diff review | `scripts/validate-todo.mjs` | scope import が無く、全タスク検証のまま。 | planned |
| AC-006 | TODO | 運用節が記載される。 | diff review | `_docs/standards/documentation_operations.md` | DD_SCOPE_BASE / fetch-depth / 権限 / --diff-filter=A / TODO 常時検証を記述。 | planned |
| INV-001 | intent | default-off で全走査。 | self-test | `scripts/test-validators.mjs` | env 未設定の既存 fixture テストが従来通り pass / fail。 | planned |
| INV-002 | intent | 追加ファイルのみ判定。 | manual QA | `DD_SCOPE_BASE=<root> deno run ... validate-frontmatter.mjs` | baseline 以降の追加 docs のみ走査される。 | planned |
| INV-003 | intent | 参照先存在は全体に対して確認。 | diff review | `scripts/validate-doc-links.mjs` | 起点のみ inScope で絞り、`exists()` は fs 全体。 | planned |
| INV-004 | intent | TODO 検証は常時全タスク。 | diff review | `scripts/validate-todo.mjs` | 変更なし。 | planned |
| INV-005 | intent | 母集合決定の集約。 | diff review | `scripts/scope.mjs` | `loadScope` が単一の解決点。 | planned |
| INV-006 | intent | 権限欠如時は全走査へフォールバック。 | unit | `scripts/scope.mjs` `readEnv` | env 読み取り例外を catch し未設定扱い。 | planned |

## Manual QA Checklist

- [ ] `DD_SCOPE_BASE` を root commit に設定し、validator がリポジトリ初期以降の追加 docs を走査することを確認する。
- [ ] `DD_SCOPE_BASE=HEAD`（追加ファイル空集合）で validator が全 docs をスキップし exit 0 になることを確認する。
- [ ] env 未設定の `./scripts/check-docs.sh` が従来通り全 docs を検証することを確認する。
- [ ] `.agents` と `.claude` の skill コピーが同期されたままであることを確認する。

## Regression Checklist

- [ ] env 未設定時、3 validator の判定結果が変更前と同一である。
- [ ] `validate-todo.mjs` がスコープの影響を受けない。
- [ ] 既存の validator fixture self-test が従来通り pass / fail する。
- [ ] `deno fmt --check scripts/*.mjs` が通過する。

## Out of Scope

- `validate-todo.mjs` のスコープ化。
- `--diff-filter=ACMR`（変更ファイル対象化）の既定採用。
- front-matter マーカー方式・ディレクトリ分離方式。
- テンプレート自身の CI でスコープを有効化すること。

## Open Questions

- None.
