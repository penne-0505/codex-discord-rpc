---
title: "QA Test Plan: Code ↔ intent traceability"
status: active
draft_status: n/a
qa_status: planned
risk: Medium
created_at: 2026-06-19
updated_at: 2026-06-19
references:
  - "_docs/intent/Workflow/code-intent-traceability/decision.md"
  - "_docs/plan/Workflow/code-intent-traceability/plan.md"
related_issues: []
related_prs: []
---

# QA Test Plan: `Code ↔ intent traceability`

## Source of Intent

- TODO: `Workflow-Feat-8`
- Plan: `_docs/plan/Workflow/code-intent-traceability/plan.md`
- Intent: `_docs/intent/Workflow/code-intent-traceability/decision.md`

## Quality Goal

コード起点でも why / why not（intent）へ到達できる導線を、テンプレートの軽量 Fast Track 哲学を壊さずに規約として定着させること。規則が全コード義務化・生パス化・テストとの二重義務化・validator 機械強制へ逸脱しないこと。

## Acceptance Criteria

- AC-001: `_docs/standards/quality_assurance.md` に「intent ↔ code traceability」節があり、ターゲット型・参照書式・テストとの線引き・強制レベル（validator 非強制）を規定する。
- AC-002: `_docs/standards/templates/intent.md` が、INV を安定 ID・コードから一行引用できる粒度で書く指針と、任意の back-reference 欄を含む。
- AC-003: `test-maintenance` / `implementation-prep` / `post-implementation` skill が、コード起点トレーサビリティの手順（参照を残す / 確認する、テストとコメントの線引き）を含む。
- AC-004: 上記 skill の変更が `.claude/skills/` と `.agents/skills/` の両方で同一である。
- AC-005: `AGENTS.md` の原則に、非自明箇所へ intent 参照を残す旨の一行がある。
- AC-006: `_docs/documentation_guide.md` に、正典と矛盾しないクイックリファレンスがある。
- AC-007: markdownlint と全 validator（frontmatter / todo / doc-links / qa）と test-validators が PASS する。

## Intent-derived Invariants

- INV-001: 規則文書は参照をターゲット型として記述し、全コード・全コメントへの義務化を要求しない。
- INV-002: 規則文書はアンカーとして安定 ID（`INV-xxx` / `AC-xxx`）を主に据え、生 doc パスのみの参照を正典としない。
- INV-003: 規則文書はテストで表明できる不変条件をテストへ、テスト化しにくい why not をコメントへ割り当て、同一条件の二重義務化を求めない。
- INV-004: 規則文書は validator によるコード参照の機械強制を要求せず、遵守を skill と review で担保すると述べる。
- INV-005: intent template は INV を安定 ID・一行引用できる粒度・断定形で書くよう求める。
- INV-006: 規則文書は grep 可能な参照接頭辞（`intent:` / `intent why-not:`）を定義する。

## Risk Assessment

- Risk level: Medium
- Risk rationale: documentation rule と複数 skill を横断変更する。失敗時の影響は agent の運用解釈の質。
- Regression risk: 既存の Fast Track 哲学や intentional-omission-risk decision の INV と矛盾する記述が混入し、小タスクへ過剰な記録義務を波及させること。
- Data safety risk: None（ドキュメント編集のみ。破壊的操作なし）。
- Security / privacy risk: None。
- UX risk: Low（contributor / agent 向けの運用文書）。
- Agent misbehavior risk: agent が規則を「全コードにコメント必須」「生パスで良い」「テストと重複して書く」「validator で弾く」と誤解し、ノイズ増大や既存哲学の破壊へ向かう可能性。

## Test Strategy

- Diff review: 正典（quality_assurance）/ intent template / 3 skill / AGENTS / guide が、ターゲット型・安定 ID・線引き・非強制を一貫して述べていること。
- Sync check: 3 skill が `.claude` と `.agents` で同一であること（diff が空）。
- Consistency check: 規則が intentional-omission-risk decision の INV-001（小タスクへ記録欄を強制しない）と矛盾しないこと。
- Validator / static check: markdownlint、全 validator、test-validators の実行。
- Agent misbehavior check: 逸脱パターン（全コード義務化 / 生パス化 / 二重義務化 / 機械強制）が規則文に現れていないことを確認。

## Test Matrix

| ID | Source | Requirement / Invariant | Test Type | Command / File | Expected Evidence | Status |
| --- | --- | --- | --- | --- | --- | --- |
| AC-001 | TODO | traceability 節が規約を規定。 | diff review | `_docs/standards/quality_assurance.md` | ターゲット型 / 書式 / 線引き / 非強制を記述。 | planned |
| AC-002 | TODO | intent template に粒度ガイド + 任意 back-ref。 | diff review | `_docs/standards/templates/intent.md` | 安定 ID 粒度ガイドと back-reference 欄が存在。 | planned |
| AC-003 | TODO | 3 skill に手順追加。 | diff review | `.claude/skills/{test-maintenance,implementation-prep,post-implementation}/SKILL.md` | コード起点トレーサビリティ手順を記述。 | planned |
| AC-004 | TODO | skill が両系で同期。 | sync check | `diff .claude/skills/<n>/SKILL.md .agents/skills/<n>/SKILL.md` | 差分なし。 | planned |
| AC-005 | TODO | AGENTS に原則一行。 | diff review | `AGENTS.md` | 非自明箇所へ intent 参照を残す原則がある。 | planned |
| AC-006 | TODO | guide にミラー。 | diff review | `_docs/documentation_guide.md` | 正典と矛盾しない要約がある。 | planned |
| AC-007 | TODO | 既存検証が PASS。 | validator | `./scripts/check-docs.sh` + markdownlint | 全 validator と markdownlint が PASS。 | planned |
| INV-001 | intent | ターゲット型維持。 | agent misbehavior check | 各規則文書 | 「全コード / 全コメント義務化」の記述がない。 | planned |
| INV-002 | intent | 安定 ID 主。 | diff review | quality_assurance / intent template | ID を主、パスを従とする書式定義がある。 | planned |
| INV-003 | intent | テストとの線引き。 | diff review | quality_assurance / test-maintenance | 二重義務化を求めない記述がある。 | planned |
| INV-004 | intent | validator 非強制。 | diff review | quality_assurance | 機械強制しないと明記。 | planned |
| INV-005 | intent | INV 粒度ガイド。 | diff review | `_docs/standards/templates/intent.md` | 一行引用できる粒度・断定形を求める。 | planned |
| INV-006 | intent | grep 可能接頭辞。 | diff review | quality_assurance | `intent:` / `intent why-not:` を定義。 | planned |

## Manual QA Checklist

- [ ] 規則を読んだ agent が、小タスク（Fast Track）に新たな記録義務を負わない解釈になることを確認する。
- [ ] `.agents` と `.claude` の 3 skill が同一であることを確認する。
- [ ] quality_assurance の書式例が、実在の INV ID 形式（`INV-001`）と整合することを確認する。
- [ ] intentional-omission-risk decision を再読し、新規則と矛盾しないことを確認する。

## Regression Checklist

- [ ] 既存 validator fixture self-test が従来通り pass / fail する。
- [ ] `deno fmt --check scripts/*.mjs` が通過する（scripts 無変更でも確認）。
- [ ] markdownlint が新規 / 変更 docs を含めて PASS する。
- [ ] 既存の standards / skills の他セクションに退行がない。

## Out of Scope

- 全コードへの参照義務化。
- リンク切れ検出 validator の実装。
- agent-workflows eval ケースの追加。
- 既存ソースコードへの遡及的コメント付与。

## Open Questions

- None.
