---
title: "QA Verification: Incremental adoption scope"
status: active
draft_status: n/a
qa_status: verified
risk: Medium
created_at: 2026-06-15
updated_at: 2026-06-15
references:
  - "_docs/intent/Workflow/incremental-adoption-scope/decision.md"
  - "_docs/qa/Workflow/incremental-adoption-scope/test-plan.md"
related_issues: []
related_prs: []
---

# QA Verification: `Incremental adoption scope`

## Summary

docs validator に opt-in / default-off のスコープ機構を追加した。母集合決定を `scripts/scope.mjs` に集約し、`validate-frontmatter` / `validate-doc-links` / `validate-qa` が共有する。env 未設定時は全走査の従来挙動を保ち、`DD_SCOPE_BASE`（git ref, `--diff-filter=A`）または `DD_SCOPE_PATHS`（明示リスト）で「導入以降に追加された docs」だけへ判定を絞れる。`validate-todo.mjs` は非スコープのまま。

## Verification Verdict

Verdict: PASS

## Commands Run

```bash
deno fmt scripts/*.mjs
bash scripts/check-docs.sh
DD_SCOPE_BASE=HEAD deno run --allow-read --allow-env --allow-run=git scripts/validate-frontmatter.mjs
DD_SCOPE_BASE=<root> deno run --allow-read --allow-env --allow-run=git scripts/validate-frontmatter.mjs
DD_SCOPE_BASE=<root> deno run --allow-read --allow-env --allow-run=git scripts/validate-doc-links.mjs
git diff --name-only --diff-filter=A <root>...HEAD | grep -E '^(_docs|_evals).*\.md$' | wc -l
grep -l 'from "./scope.mjs"' scripts/validate-frontmatter.mjs scripts/validate-doc-links.mjs scripts/validate-qa.mjs
grep -c 'scope.mjs' scripts/validate-todo.mjs
git diff --check
```

Result:

```text
deno fmt: exit 0; Checked 6 files (no reformatting needed).
bash scripts/check-docs.sh: exit 0; all validators + fixture self-tests + 2 scope tests passed.
DD_SCOPE_BASE=HEAD validate-frontmatter: exit 0; added set empty -> all docs skipped.
DD_SCOPE_BASE=<root> validate-frontmatter: exit 0; scoped to 44 added docs, all valid.
DD_SCOPE_BASE=<root> validate-doc-links: exit 0.
git diff added _docs/_evals md count: 44.
grep import: frontmatter / doc-links / qa all match scope.mjs import.
grep validate-todo scope.mjs: 0 (no scope coupling).
git diff --check: exit 0; no whitespace errors.
```

## Automated Test Results

| Command / Test | Result | Notes |
| --- | --- | --- |
| `bash scripts/check-docs.sh` | PASS | fmt + 3 scoped validators (env 未設定 = 全走査) + self-test。 |
| `scope out-of-scope invalid fixture is skipped` | PASS | `DD_SCOPE_PATHS` が除外した invalid fixture で exit 0。 |
| `scope in-scope invalid fixture still fails` | PASS | `DD_SCOPE_PATHS` が含める invalid fixture で exit 非 0。 |
| `DD_SCOPE_BASE=HEAD` frontmatter | PASS | 空 scope で全 skip、exit 0。 |
| `DD_SCOPE_BASE=<root>` frontmatter / doc-links | PASS | 追加 44 docs を走査、exit 0。 |

## Manual QA Results

| Checklist Item | Result | Notes |
| --- | --- | --- |
| `DD_SCOPE_BASE` を root に設定し追加 docs のみ走査される。 | PASS | git diff の追加集合 44 件と一致。 |
| `DD_SCOPE_BASE=HEAD`（空集合）で全 skip し exit 0。 | PASS | 追加集合 0 件、exit 0。 |
| env 未設定の `check-docs.sh` が全 docs を従来通り検証。 | PASS | スコープ無効で全走査、exit 0。 |
| `.agents` と `.claude` の skill コピーが同期。 | PASS | skills は未変更。 |

## Acceptance Criteria Coverage

| ID | Result | Evidence |
| --- | --- | --- |
| AC-001 | PASS | env 未設定で `check-docs.sh` の 3 validator が従来通り全走査して exit 0。 |
| AC-002 | PASS | scope test `out-of-scope invalid fixture is skipped` が exit 0。 |
| AC-003 | PASS | scope test `in-scope invalid fixture still fails` が exit 非 0。 |
| AC-004 | PASS | `grep -l 'from "./scope.mjs"'` が frontmatter / doc-links / qa を返す。 |
| AC-005 | PASS | `grep -c 'scope.mjs' scripts/validate-todo.mjs` が 0。 |
| AC-006 | PASS | `_docs/standards/documentation_operations.md` に「段階的導入スコープ」節を追加。 |

## Invariant Coverage

| ID | Result | Evidence |
| --- | --- | --- |
| INV-001 | PASS | env 未設定で既存 fixture self-test と docs 検証が従来通り通過。 |
| INV-002 | PASS | `DD_SCOPE_BASE` の追加集合のみ走査。空集合は全 skip。skip/fail 判別は DD_SCOPE_PATHS test で確認。 |
| INV-003 | PASS | `validate-doc-links.mjs` は起点のみ `inScope` で絞り、`exists()` は fs 全体。`DD_SCOPE_BASE=<root>` で doc-links が exit 0。 |
| INV-004 | PASS | `validate-todo.mjs` に scope import なし。 |
| INV-005 | PASS | `scripts/scope.mjs` の `loadScope` が単一の母集合解決点。 |
| INV-006 | PASS | `scope.mjs` の `readEnv` が env 読み取り例外を catch し未設定扱い（全走査）へフォールバック。 |

## Deferred / Not Covered

| ID | Reason | Follow-up |
| --- | --- | --- |
| INV-002 (git skip/fail discrimination) | 全 committed docs が valid のため、git 経路単体では「絞って fail させる」直接証拠を出せない。skip/fail の判別ロジックは `DD_SCOPE_PATHS` self-test で決定的に確認済み。 | None（self-test で恒久回帰カバー済み）。 |

## Residual Risks

None

## Follow-up TODOs

None
