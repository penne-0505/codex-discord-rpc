---
title: "QA Verification: Code ↔ intent traceability"
status: active
draft_status: n/a
qa_status: verified
risk: Medium
created_at: 2026-06-19
updated_at: 2026-06-19
references:
  - "_docs/intent/Workflow/code-intent-traceability/decision.md"
  - "_docs/qa/Workflow/code-intent-traceability/test-plan.md"
related_issues: []
related_prs: []
---

# QA Verification: `Code ↔ intent traceability`

## Summary

コード起点でも intent（why / why not）へ到達できる参照ルールを、ターゲット型・安定 ID アンカー・テストとの線引き・validator 非強制として定義し、`_docs/standards/quality_assurance.md` を正典に、intent template / 3 skill（`.claude` と `.agents` 両系）/ AGENTS.md / documentation_guide へ一貫展開した。runtime コードは変更していない。検証は diff review と既存品質ゲート（markdownlint + 全 validator + test-validators）で行った。

## Verification Verdict

Verdict: PASS

## Commands Run

```bash
bash scripts/check-docs.sh
npx markdownlint-cli2 "_docs/**/*.md" "_evals/**/*.md" "README.md" "AGENTS.md" "TODO.md" "QUICKSTART.md" "!_docs/archives/**/*" "!_docs/standards/templates/**/*" --config .markdownlint.jsonc
for s in test-maintenance implementation-prep post-implementation; do diff -q .claude/skills/$s/SKILL.md .agents/skills/$s/SKILL.md; done
grep -c "intent ↔ code traceability" _docs/standards/quality_assurance.md AGENTS.md _docs/documentation_guide.md
grep -c "Enforced in (optional)" _docs/standards/templates/intent.md
```

Result:

```text
bash scripts/check-docs.sh: exit 0; 全 validator + fixture self-test + scope test が PASS。
markdownlint: 54 files, 0 error(s)。
skill diff: 3 skill とも .claude / .agents で差分なし。
grep traceability 節: quality_assurance=1, AGENTS=1, guide=2。
grep intent template back-ref 欄: 1。
```

## Automated Test Results

| Command / Test | Result | Notes |
| --- | --- | --- |
| `bash scripts/check-docs.sh` | PASS | frontmatter / todo / doc-links / qa validator と fixture self-test が exit 0。 |
| markdownlint (CI globs) | PASS | 54 files、0 error。 |
| skill sync `diff -q` ×3 | PASS | `.claude` と `.agents` が同一。 |

## Manual QA Results

| Checklist Item | Result | Notes |
| --- | --- | --- |
| Fast Track に新たな記録義務を負わせない解釈になる。 | PASS | 正典・skill・AGENTS いずれも「ターゲット型」「全コード義務化しない」と明記。 |
| `.agents` と `.claude` の 3 skill が同一。 | PASS | `diff -q` 差分なし。 |
| 書式例が実在の INV ID 形式（`INV-001`）と整合。 | PASS | `// intent: INV-003 (Workflow/<slug>)` 形式で統一。 |
| intentional-omission-risk decision と矛盾しない。 | PASS | 新規則は同 decision の防御をコードへ降ろす位置づけで、INV-001（小タスクへ記録欄を強制しない）と整合。 |

## Acceptance Criteria Coverage

| ID | Result | Evidence |
| --- | --- | --- |
| AC-001 | PASS | `quality_assurance.md` に「intent ↔ code traceability」節（ターゲット型 / 書式 / 線引き / 非強制）を追加。grep 一致。 |
| AC-002 | PASS | `templates/intent.md` に INV 粒度ガイドと `Enforced in (optional)` back-reference 欄を追加。 |
| AC-003 | PASS | `test-maintenance`（Test vs Comment Split）/ `implementation-prep`（anchor step）/ `post-implementation`（完了前チェック）に手順追加。 |
| AC-004 | PASS | 3 skill とも `.claude` / `.agents` で `diff -q` 差分なし。 |
| AC-005 | PASS | `AGENTS.md` 原則に intent 参照の一行を追加。 |
| AC-006 | PASS | `documentation_guide.md` に正典と矛盾しないミラー節を追加。 |
| AC-007 | PASS | `check-docs.sh` exit 0、markdownlint 0 error。 |

## Invariant Coverage

| ID | Result | Evidence |
| --- | --- | --- |
| INV-001 | PASS | 正典・AGENTS・guide が「ターゲット型」「全コード・全コメントへの一律義務化はしない」と明記。 |
| INV-002 | PASS | 書式定義が安定 ID を主、生パスを正典にしないと記述。 |
| INV-003 | PASS | 正典「テストとコメントの線引き」と test-maintenance「Test vs Comment Split」が二重義務化を否定。 |
| INV-004 | PASS | 正典「強制レベル」が validator 非強制・skill / review 担保と明記。 |
| INV-005 | PASS | intent template が安定 ID・一行引用粒度・断定形を要求。 |
| INV-006 | PASS | 正典が `intent:` / `intent why-not:` 接頭辞を定義。grep 一致。 |

## Deferred / Not Covered

| ID | Reason | Follow-up |
| --- | --- | --- |
| 規則の実コードへの適用 | テンプレート本体に対象 runtime コードがないため、実コードへのアンカー付与は本タスクの検証対象外。 | 利用先プロジェクトで運用時に適用。 |
| リンク切れ検出 validator | intent decision の Non-Goal。任意・default-off の将来拡張。 | Follow-up TODO 候補（未起票）。 |
| agent-workflows eval ケース | intent decision の Non-Goal。 | Follow-up TODO 候補（未起票）。 |

## Residual Risks

None

## Follow-up TODOs

- （任意）コード → intent 参照のリンク切れ検出 validator（default-off）。
- （任意）`_evals/agent-workflows/cases/` に「コード起点で intent に到達できるか」ケースを追加。
