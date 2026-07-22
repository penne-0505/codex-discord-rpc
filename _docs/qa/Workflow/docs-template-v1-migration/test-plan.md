---
title: "QA Test Plan: Docs-driven template v1.0.0 migration"
status: active
draft_status: n/a
qa_schema: 2
qa_status: planned
risk: High
created_at: 2026-07-22
updated_at: 2026-07-22
references:
  - "_docs/archives/plan/Workflow/docs-template-v1-migration/plan.md"
  - "_docs/intent/Workflow/docs-template-v1-migration/decision.md"
related_issues: []
related_prs: []
---

# QA Test Plan: Docs-driven template v1.0.0 migration

## Source of Intent

- TODO: `Workflow-Chore-12`
- Plan: `_docs/archives/plan/Workflow/docs-template-v1-migration/plan.md`
- Intent: `_docs/intent/Workflow/docs-template-v1-migration/decision.md`

## Decision Review Scope

- DEC-001: B / U / P provenance、tag/full SHA、lock advancement順。
- DEC-002: project customizationとruntime/service pathの保全。
- DEC-003: compatibilityとstrict schemaの分離、semantic migration限定。
- DEC-004: hookのguardrail / non-mutating boundary。
- DEC-005: template self-metaの除外とobsolete record整理。

## Quality Goal

v1.0.0のworkflow baselineを再現可能に統合しながら、Codex Discord RPCのruntime、service、project recordを変更せず、次回migrationのBをlockで確定する。

## Acceptance Criteria

- AC-001〜AC-009は`TODO.md`の`Workflow-Chore-12`を正典とする。

## Intent-derived Invariants

- INV-001: lockはv1.0.0とU full SHAの組を記録する。
- INV-002: runtime / service sourceとCore project docsは変更しない。
- INV-003: existing Core legacy docsをbulk schema conversionしない。
- INV-004: template self-meta docsをactive treeへ残さない。

## Risk Assessment

- Risk level: High
- Migration / compatibility: validator、CI、hooks、skillsの整合不良でcontributor workflowが停止し得る。
- Regression: shared root / standardsのblind replacementでproject commandやprivacy / service boundaryを失う可能性。
- Data safety: isolated clean worktreeだけを変更し、active checkout、live service、remoteは操作しない。
- Security: hook scriptを実行前にレビューし、secret-like path、destructive command、archive boundaryのguardだけを確認する。
- Agent misbehavior: branch混入、moving tip利用、blind replacement、premature lock、bulk schema edit、template self-meta導入を明示的に拒否する。

## Test Strategy

- Baseline: migration write前の`./scripts/check-docs.sh`結果を保持する。
- Compatibility: final wrapper、validator fixture、agent hook unit / smoke、Deno fmt、markdownlint、paired skill比較。
- Strict schema: new migration docsのschema v2 validationとexisting Core docのblob不変を別に確認する。
- Project regression: Ruff、pytest、compileall、build、CLI render、installer dry-runを非liveで実行する。
- Diff / provenance: inventory reconciliation、source path diff、meta refs、lock JSON、git diff check、single commit / no pushを確認する。

## Test Matrix

| ID | Source | Requirement / Optional Invariant | Test Type | Command / File | Expected Evidence | Status |
| --- | --- | --- | --- | --- | --- | --- |
| AC-001 | TODO | B / U / Pとtag resolution | static | `git rev-parse`, plan, lock | full SHAが一致 | verified |
| AC-002 | TODO | 122 upstream/project inventoryとmigration-created 8 artifact ledger | diff review | Plan inventory / artifact ledger / P→C set audit | union全pathと追加artifactを分離分類し、実変更90 pathの未分類0 | verified |
| AC-003 | TODO | project customization保全 | diff review | source / Core docs / root docs | runtime変更0、project節保持 | verified |
| AC-004 | TODO | U workflow integration | automated | wrapper、hook tests、paired cmp | 全check PASS | verified |
| AC-005 | TODO | template self-meta除外 | static | `rg`, path existence | obsolete refsとmeta path 0 | verified |
| AC-006 | TODO | compatibility / strict schema分離 | validator + review | intent / QA validator、Core blob cmp | new v2 PASS、existing legacy不変 | verified |
| AC-007 | TODO | documented checks | automated | docs / project command set | 全非live check PASS | verified |
| AC-008 | TODO | behavior不変とlock順 | diff + history review | `git diff`, lock review | source変更0、lockはU | verified |
| AC-009 | TODO | local single commit | git | `git log`, remote status | 1 commit、pushなし | covered |
| INV-001 | DEC-001 | tag/full SHA lock | static | `docs-template.lock.json` | exact pair | verified |
| INV-002 | DEC-002 | runtime / Core docs不変 | blob comparison | `git diff -- <paths>` | empty | verified |
| INV-003 | DEC-003 | bulk conversion禁止 | blob comparison | Core intent / QA | cutoff blobと一致 | verified |
| INV-004 | DEC-005 | self-meta不在 | static | `test ! -e`, `rg` | lifecycle / obsolete records不在 | verified |

## Manual QA Checklist

- [x] AGENTSのproject command / privacy boundaryが保持される。
- [x] README / Quickstart / guideのservice installerとrecovery手順が保持される。
- [x] docs CIのtriggerとmarkdownlint scopeを保持したままU validatorを呼ぶ。
- [x] hookがdocsを自動更新せず、runtime commandを実行しない。
- [x] lock作成前にcompatibility checksがPASSしている。

## Regression Checklist

- [x] `src/**`、installer、unitにdiffがない。
- [x] Core intent / QA / guideとhistorical verification command/resultを変更しない。
- [x] paired skillsがbyte-identical。
- [x] deleted meta pathを参照するproject docがない。
- [x] active checkoutとlive serviceを操作していない。

## High-risk Checklist

- [x] Rollback: migration commitを採用しないだけでcutoff Pへ戻せる。
- [x] Data safety: active checkout、live service、user config、remoteを変更していない。
- [x] Security: imported hookを実行前にreviewし、secret読み取りや外部送信を行わない。
- [x] Recovery: validator / CI incompatibilityはlock作成前に検出し、Pとinventoryから再開できる。
- [x] Compatibility: legacy Core docsがnew validatorで引き続き受理される。
- [x] Provenance: tag resolution不一致やinventory未解決があればmigrationを完了しない。

## Out of Scope

- Live Discord / systemd検証。
- Existing Core intent / QAのschema v2再設計。
- Templateのlifecycle-self-audit履歴の導入。
- Push / PR。

## Open Questions

None.
