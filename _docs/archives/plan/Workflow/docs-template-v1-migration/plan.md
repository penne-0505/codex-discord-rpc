---
title: "Plan: Docs-driven template v1.0.0 migration"
status: active
draft_status: n/a
created_at: 2026-07-22
updated_at: 2026-07-22
references:
  - "_docs/intent/Workflow/docs-template-v1-migration/decision.md"
  - "_docs/qa/Workflow/docs-template-v1-migration/test-plan.md"
related_issues: []
related_prs: []
---

# Plan: Docs-driven template v1.0.0 migration

## Overview

pre-v1.0.0で導入されたdocs-driven templateを、project cutoffとupstream releaseをfull SHAで固定し、project固有変更を保全するthree-way migrationとしてv1.0.0へ更新する。

## Scope

- Source: `https://github.com/penne-0505/docs_driven_dev_template.git`
- B: `e6dc4331a81af21494208610b22ef2d9ecdce885`（前回採用commit、high confidence）
- U: tag `v1.0.0` / `f71e9ab20466ea2972158334261f5ae2b2265754`
- P: clean `origin/main` cutoff `fc463525b91dac8e36ab8c817cb8d71c9461889d`
- Worktree: `/tmp/docs-template-v1-rollout/codex-discord-rpc`
- Included lane: `B..U`だけ。moving branch tipと他branchは含めない。

## Non-Goals

- Python runtime、Discord IPC、installer、systemd serviceのbehavior変更。
- active checkout、live user service、remote branchの更新。
- legacy project intent / QAの機械的なschema v2一斉変換。
- Uで追加されたtemplate自身のlifecycle-self-audit plan / intent / QA履歴の導入。

## Requirements

- compatibility migrationを先に通し、lockはその後の最後のwriteにする。
- shared customized fileはB / U / Pを照合してmergeし、wholesale replacementしない。
- project-only pathとruntime sourceは保持する。
- template-only obsolete recordは、B blob一致とproject参照解消を確認したpathだけ削除する。
- schema v2は新規migration docsへ適用し、既存legacy docsはsemantic changeがない限り維持する。

## Three-way Inventory

全122 pathにresolutionを割り当てた。`apply`はBと一致するupstream-owned pathへのU delta適用、`merge`は三者比較、`keep`はproject状態維持、`remove`は参照解消後のtemplate meta整理、`defer`は今回なしを表す。

### Apply: upstream modified / project upstream-unmodified (39)

`.agents/skills/{docs-cleanup,docs-prep,implementation-prep,post-implementation,qa-prep,qa-review,test-maintenance}/SKILL.md`; `.claude/skills/`の同7 path; `.github/workflows/docs-ci.yml`; `_docs/documentation_guide.md`; `_docs/standards/quality_assurance.md`; `_docs/standards/templates/{intent,plan,qa-test-plan,qa-verification}.md`; `_evals/agent-workflows/{README.md,expected-invariants.md}`; `_evals/agent-workflows/cases/{archive-flow,breaking-change,historical-prompt-not-operational,intentional-omission-risk,medium-feature,qa-prep-from-intent,refactor-behavior-preservation,small-bug,stale-draft-cleanup}.md`; `_evals/validator-fixtures/README.md`; `scripts/{check-docs.sh,scope.mjs,test-validators.mjs,validate-doc-links.mjs,validate-frontmatter.mjs,validate-qa.mjs}`。

### Apply: upstream added operational paths (20)

`.agents/skills/{docs-inventory,docs-template-migration}/SKILL.md`; `.claude/skills/{docs-inventory,docs-template-migration}/SKILL.md`; `.claude/settings.json`; `.codex/hooks.json`; `_evals/agent-workflows/cases/{experimental-baseline,misleading-optimization,rationale-preserving-change,template-version-migration}.md`; `_evals/validator-fixtures/intent/invalid/{missing-why,orphan-invariant}.md`; `_evals/validator-fixtures/intent/valid/decision.md`; `_evals/validator-fixtures/links/valid-reference-anchor.md`（project Quickstartの同名節anchorへ適応）; `_evals/validator-fixtures/qa/invalid/v2-missing-decision-scope.md`; `docs-template.lock.example.json`; `scripts/{agent-workflow-hook.mjs,test-agent-workflow-hook.mjs,test-agent-workflow-smoke.mjs,validate-intent.mjs}`。

### Merge: upstream modified / project customized-shared (13)

`AGENTS.md`; `QUICKSTART.md`; `README.md`; `TODO.md`; `_docs/standards/{documentation_guidelines,documentation_operations}.md`; `_evals/validator-fixtures/qa/invalid/{missing-invariant,qa-archive-path,status-verdict-mismatch,verification-in-progress-status,verification-missing-test-plan-reference}.md`; `_evals/validator-fixtures/qa/valid/{test-plan,verification-pass}.md`。

`README.md`はupstream template紹介をproject READMEへ混ぜずkeepし、それ以外はproject固有部分を保持しながらUのworkflow/schema差分をmergeする。

### Keep: project-only (28)

`.gitignore`; `config.example.toml`; `packaging/systemd/codex-discord-rpc.service.in`; `pyproject.toml`; `uv.lock`; `scripts/install-user-service.sh`; `_docs/archives/plan/Core/codex-rich-presence/plan.md`; `_docs/guide/Core/codex-rich-presence/usage.md`; `_docs/intent/Core/codex-rich-presence/decision.md`; `_docs/qa/Core/codex-rich-presence/{test-plan,verification}.md`; `src/codex_discord_rpc/{__init__,cli,config,git_info,phases,presence,project_detection,rpc,state}.py`; `tests/{test_cli,test_config,test_git_info,test_presence,test_project_detection,test_rpc,test_service,test_state}.py`。

### Remove: upstream removed / project upstream-unmodified template meta (11)

`_docs/intent/Workflow/{code-intent-traceability,incremental-adoption-scope,intentional-omission-risk}/decision.md`; `_docs/plan/Workflow/{code-intent-traceability,incremental-adoption-scope}/plan.md`; `_docs/qa/Workflow/{code-intent-traceability,incremental-adoption-scope,intentional-omission-risk}/{test-plan,verification}.md`。

Uのstandardsとfixtureへcanonical authorityを移し、project参照が残らないことを確認してから削除する。

### Keep absent: upstream removed / project already absent (7)

`.agents/skills/frontend-design/SKILL.md`; `.claude/skills/frontend-design/SKILL.md`; `_docs/intent/Template/intent-qa-finalization/decision.md`; `_docs/plan/Template/intent-qa-finalization/plan.md`; `_docs/qa/Template/intent-qa-finalization/{test-plan,verification}.md`; `_docs/standards/jj_workflow.md`。

### Keep absent: U-added template self-meta (4)

`_docs/intent/Workflow/lifecycle-self-audit/decision.md`; `_docs/plan/Workflow/lifecycle-self-audit/plan.md`; `_docs/qa/Workflow/lifecycle-self-audit/{test-plan,verification}.md`。

## Migration-created Artifact Ledger

次の8 artifactはB→U / B→Pの122 path unionには含まれない。このmigration自身がproject-local evidence、compatibility fixture、またはprovenanceとして作成したため、最終diff監査では122 path inventoryと分離して扱う。最終監査境界は`122 upstream/project inventory + 8 migration-created artifacts`であり、B→U / B→P inventoryの件数を130へ読み替えない。

| Artifact | Classification | Lifecycle / Resolution | Rationale |
| --- | --- | --- | --- |
| `_docs/archives/plan/Workflow/docs-template-v1-migration/plan.md` | project-created migration evidence | add / archive後keep | Three-way inventoryと作業契約を保持するtemporary Planのarchive。 |
| `_docs/intent/Workflow/docs-template-v1-migration/decision.md` | project-created decision record | add / keep active | Project customization、schema、hook、meta-doc境界のWhyを保持する。 |
| `_docs/qa/Workflow/docs-template-v1-migration/test-plan.md` | project-created QA record | add / keep active | Migration AC / DEC / INVとverification pathを保持する。 |
| `_docs/qa/Workflow/docs-template-v1-migration/verification.md` | project-created QA evidence | add / keep active | 実行済みcheck、compatibility / strict schema判定、残リスクを保持する。 |
| `docs-template.lock.json` | project-created upstream provenance lock | add / keep tracked | Compatibility PASS後にU tagとfull SHAを固定し、次回migrationのBにする。 |
| `_evals/validator-fixtures/frontmatter/known/intent-schema.md` | project-created compatibility fixture | add / keep tracked | Intent pathで正式`intent_schema` markerがunknown warningにならないことを固定する。 |
| `_evals/validator-fixtures/frontmatter/known/qa-schema.md` | project-created compatibility fixture | add / keep tracked | QA pathで正式`qa_schema` markerがunknown warningにならないことを固定する。 |
| `_evals/validator-fixtures/frontmatter/unknown/future-schema.md` | project-created warning fixture | add / keep tracked | 未知markerへのwarningを維持し、known-field allowlistの過剰拡張を防ぐ。 |

## Tasks

1. Uのvalidator / fixtureをlegacy-compatible modeで導入し、既存project docsをschema変換せず検証する。
2. paired skills、hooks、CI、standards、templates、root guidanceをpath-by-pathで統合する。
3. template meta recordの参照をUのcanonical standards / fixturesへ移し、provenance確認済みpathだけ削除する。
4. compatibility checksを通し、existing legacy docsとnew schema v2 docsの境界を確認する。
5. lockをUで作成し、closure verificationを実行する。

## QA Plan

- Risk: High（validator / CI / migration / workflow変更）。
- QA: `_docs/qa/Workflow/docs-template-v1-migration/test-plan.md`
- Agent misbehavior: branch混入、blind replacement、premature lock、bulk schema edit、template self-meta混入を明示的に確認する。
- Runtime preservation: source pathのdiff不在とproject test / buildで確認する。

## Deployment / Rollout

isolated worktree内で1 commitを作成する。push、active checkout変更、live service操作は行わない。rollbackはcommitを採用しないことで完結する。
