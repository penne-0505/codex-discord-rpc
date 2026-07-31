---
title: "QA Test Plan: Docs-driven template v1.2.0 migration"
status: active
draft_status: n/a
qa_schema: 2
qa_status: planned
risk: High
created_at: 2026-08-01
updated_at: 2026-08-01
references:
  - "_docs/archives/plan/Workflow/docs-template-v1-2-migration/plan.md"
  - "_docs/intent/Workflow/docs-template-v1-2-migration/decision.md"
related_issues: []
related_prs: []
---

# QA Test Plan: Docs-driven template v1.2.0 migration

## Source of Intent

- Completed TODO: `Workflow-Chore-13`（PASS後にTODO lifecycle規則で削除）
- Plan: `_docs/archives/plan/Workflow/docs-template-v1-2-migration/plan.md`
- Intent: `_docs/intent/Workflow/docs-template-v1-2-migration/decision.md`

## Decision Review Scope

- DEC-001: annotated tag / peeled commit、B / U / P、branch containment、lock advancement順。
- DEC-002: U consumer projection、project customization、runtime / service / privacy contract保全。
- DEC-003: `.mjs`→`.ts` semantic port、削除許可集合、obsolete entrypoint不在。
- DEC-004: legacy compatibilityとstrict schemaの分離、bulk conversion不在。
- DEC-005: template self-meta除外とproject migration evidence保持。
- DEC-006: workflow-sensitive risk通知、working-tree evidence、Risk判定を自動化しない境界。

## Quality Goal

v1.2.0のconsumer-facing workflow baselineを再現可能に統合し、Codex Discord RPC固有のruntime・運用・privacy契約を変更せず、validator / hook / CIを一つのTypeScript経路へ更新する。

## Acceptance Criteria

- AC-001: B / U / Pとremote branch containmentを再現可能に固定する。
- AC-002: three-way inventoryの全pathへresolutionとrationaleを割り当てる。
- AC-003: Uのconsumer-facing `starter/`内容だけをrootへ投影し、template self-metaを除外する。
- AC-004: workflow filesを統合しながらproject root / Core customizationを保全する。
- AC-005: semantic port後に許可済み旧`.mjs` 10 pathだけを削除する。
- AC-006: compatibility migrationとstrict schema migrationを別々に判定する。
- AC-007: validator、fixture、hook、paired skill、markdownのdocs gateを通す。
- AC-008: runtime diffを入れず、project regression checksを通す。
- AC-009: compatibility PASS後にlockをU exact pairへ進めて再検証する。

## Intent-derived Invariants

- INV-001: lockはv1.2.0とU peeled full SHAのexact pairを記録する。
- INV-002: runtime / service / Core docs / project root guidanceを保全する。
- INV-003: deletion集合は許可済み`.mjs` 10件だけである。
- INV-004: existing Core intent / QAをbulk schema conversionしない。
- INV-005: template router / `starter/` / lifecycle-self-audit docsをactive treeへ残さない。

## Risk Assessment

- Risk level: High。
- Migration / compatibility: TypeScript command、Deno permissions、CI、hook configの不整合でdocs workflowが停止し得る。
- Regression: `starter/` restructuringをraw treeとして導入するとproject `AGENTS.md`、TODO、root docsがtemplate開発用内容に置換され得る。
- Data safety: ownerが許可した10 path以外のdeletionは禁止。lockはcompatibility PASSまで変更しない。
- Security: external U skill / hook / scriptは実行前にread reviewし、secret-like dataや外部送信を追加していないことを確認する。
- Agent misbehavior: branch mixing、moving tip、blind replacement、root router導入、premature lock、bulk schema edit、削除範囲逸脱を明示的に確認する。
- Rollback: uncommitted git diffとして保持し、ownerの明示指示なしにreset / checkoutによる復元は行わない。

## Test Strategy

- Baseline: migration write前の`./scripts/check-docs.sh` PASSを記録済み。
- Preparation: TODO / Plan / Intent / QAを現行validatorで検証する。
- Compatibility gate 1: UのTypeScript validator / fixture / runnerを導入し、standards semantic mergeとold `.mjs`削除前にexisting docsを検証する。
- Compatibility gate 2: skills / hooks / CI / standards / shared docs mergeとold `.mjs`削除後にfull wrapper、hook unit / smoke、fixtures、paired skills、markdownlintを実行する。
- Strict schema: new migration docsのschema v2 validationとexisting Core doc blob不変を別に確認する。
- Project regression: Ruff、pytest、compileall、build、CLI render、doctor、installer dry-runをnon-liveで実行する。
- Diff / provenance: deleted path allowlist、project-only paths、secret-like additions、lock JSON、tag resolution、git diff checkをreviewする。

## Test Matrix

| ID | Source | Requirement / Optional Invariant | Test Type | Command / File | Expected Evidence | Status |
| --- | --- | --- | --- | --- | --- | --- |
| AC-001 | TODO | B / U / Pとtag resolution | static | `git ls-remote --tags`, `git rev-parse`, Plan | exact SHA対応 | verified |
| AC-002 | TODO | three-way inventory completeness | diff review | Plan inventory、final changed-path audit | unresolved path 0 | verified |
| AC-003 | TODO | consumer projection / meta exclusion | static | final path list、root guidance review | `starter/`とrouter不在 | verified |
| AC-004 | TODO | shared customization保全 | diff review | B / U / P comparison | project sections保持 | verified |
| AC-005 | TODO | authorized `.mjs` deletionだけ | static + test | `git diff --diff-filter=D --name-only`、`.ts` tests | exact 10 paths | verified |
| AC-006 | TODO | compatibility / strict schema分離 | validator + blob review | wrapper、Core docs comparison | separate PASS / non-PASS verdict | verified |
| AC-007 | TODO | docs workflow gate | automated | `./scripts/check-docs.sh`, markdownlint, `cmp` | all PASS | verified |
| AC-008 | TODO | project behavior preservation | automated + diff | Ruff、pytest、build、CLI、installer、runtime path diff | all PASS、runtime diff 0 | verified |
| AC-009 | TODO | final lock advancement | static | lock JSON、remote tag resolution、diff history | compatibility後のexact pair | verified |
| INV-001 | DEC-001 | exact tag / SHA lock | static | `docs-template.lock.json` | v1.2.0 exact pair | verified |
| INV-002 | DEC-002 | runtime / service / Core docs保全 | blob comparison | cutoff HEADとのpath diff | unauthorized semantic change 0 | verified |
| INV-003 | DEC-003 | deletion allowlist | static | deleted path set comparison | exact 10、extra 0 | verified |
| INV-004 | DEC-004 | bulk conversion禁止 | blob comparison | existing Core intent / QA | cutoff blobsを維持 | verified |
| INV-005 | DEC-005 | template self-meta不在 | static | `test ! -e`, `rg` | prohibited paths / refs 0 | verified |

## Manual QA Checklist

- [x] `AGENTS.md`のproject command、privacy、live-service boundaryが保持される。
- [x] README / Quickstartのproduct onboardingがtemplate starter説明へ置換されない。
- [x] `.ts` scriptsがexternal network送信、secret読取、docs自動更新を追加していない。
- [x] hookはRisk候補を通知するがRiskを自動確定せず、scope拡張権限を持たない。
- [x] deleted pathは明示許可済み10件だけである。
- [x] lock writeがcompatibility gateより後である。

## Regression Checklist

- [x] Existing TODO、intent、QA、link fixturesが引き続きvalidatorを通る。
- [x] Hook destructive-command guardとclosure auditがunit / smokeを通る。
- [x] `.agents` / `.claude`の9 skill pairがbyte-identicalである。
- [x] Docs CIがTypeScript commandsと必要なDeno permissionsを使う。
- [x] 初期化済みdownstreamで成立しない`starter/**/*.md` globと`starter-expansion` jobをDocs CIへ入れない。
- [x] Python unit tests、lint、build、CLI static command、installer dry-runがPASSする。
- [x] Runtime / packaging / Core docsにmigration由来のdiffがない。

## High-risk Checklist

- [x] Rollback: compatibility failure時はlockを進めず、cutoff Pとthree-way inventoryから再開できる。
- [x] Recovery: `.mjs`削除後の不整合はB / P / Uのblobと許可済みpath一覧から診断できる。
- [x] Data safety: deleted path集合が許可済み旧`.mjs` 10件と一致し、ほかのfile deletionがない。
- [x] Security / privacy: imported hook / validatorにsecret読取、外部送信、project privacy boundaryの緩和がない。
- [x] Compatibility: existing project docs、hooks、CI、project regressionがnew TypeScript entrypointでPASSする。

## Out of Scope

- Live Discord connectionとsystemd user service restart。
- Existing Core docsのsemantic schema redesign。
- Commit、push、GitHub Actionsのremote run。
- Upstream branchまたはreleaseの作成・変更。

## Open Questions

None. 旧`.mjs` 10 pathの削除はownerが明示許可済みであり、そのほかの削除は禁止されている。
