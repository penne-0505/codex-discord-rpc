---
title: "Plan: Docs-driven template v1.2.0 migration"
status: active
draft_status: n/a
created_at: 2026-08-01
updated_at: 2026-08-01
references:
  - "_docs/intent/Workflow/docs-template-v1-2-migration/decision.md"
  - "_docs/qa/Workflow/docs-template-v1-2-migration/test-plan.md"
related_issues: []
related_prs: []
---

# Plan: Docs-driven template v1.2.0 migration

## Overview

現在のv1.0.0 provenance baselineからv1.2.0へ、project cutoffとupstream releaseをfull SHAで固定したthree-way migrationを行う。v1.2.0で導入されたTypeScript validator、frontmatter検査、workflow-sensitive risk通知、consumer-facing filesの`starter/`分離をdownstream project向けに投影し、Codex Discord RPC固有のruntime、service、privacy、root guidanceを保持する。

## Scope

- Source: `https://github.com/penne-0505/docs_driven_dev_template.git`
- B: tag `v1.0.0` / tag object `6a393ae11dbada5ecc38994762cb0710e7d4849d` / peeled commit `f71e9ab20466ea2972158334261f5ae2b2265754`
- U: tag `v1.2.0` / tag object `6fe10abaf7b420bf667c7b51a7b8c344853d52ab` / peeled commit `a7fb411edb8974d0c4418fc675edc829c7600728`
- P: clean HEAD `598418795d684b014b660f9c78842705e1856aa5`
- Cutoff: 2026-08-01 01:46:34 JST、staged / unstaged / untracked manifestはいずれも空。
- Destination: active tree `/home/penne/dev/active/codex-discord-rpc`。
- Parallel ownership: parallel writerなし。migration pathはこの作業だけが変更する。
- Included lane: `v1.0.0..v1.2.0`。
- Remote branch heads: `main`=`a7fb411edb8974d0c4418fc675edc829c7600728`、`agent/why-first-intent-scope`=`511f44e178fc923423d303efb6186091083a2b78`、`codex/metacognitive-audit-hooks`=`34ac6a40f86a8900c9c3bccca7411d56d56b39af`はいずれもUに包含される。excluded branch headはない。
- Recommended release evidence: remoteの最新tagがv1.2.0であり、Uの`docs-template.lock.example.json`もv1.2.0を指定する。GitHub Releaseオブジェクトはないためtagをimmutable update unitとする。

## Non-Goals

- Python runtime、Discord IPC、installer、systemd user service、live Discord stateの変更。
- project README / Quickstartをupstream template紹介へ置き換えること。
- template repository開発用のroot router、`starter/` directory、template self-development recordの導入。
- 既存Core intent / QAの意味を再構成しないままschema markerだけを追加するbulk migration。
- commit、push、release、live user service操作。
- 許可された旧`.mjs` 10ファイル以外の削除。

## Requirements

- shared pathをwholesale replacementせず、B / U / Pのrelationに応じてapply / merge / keep / removeを選ぶ。
- Uのconsumer snapshotは`starter/<path>`をproject rootの`<path>`へ投影し、rootのtemplate-development routerより優先する。
- imported skill、hook、validatorを実行前にreviewし、existing docsへのcompatibility gateをschema semantic editより先に通す。
- `.mjs`→`.ts`でP固有差分がある場合は対応する`.ts`へ意味を移してから、明示許可された旧pathだけを削除する。
- lockはcompatibility PASS後の最後のmigration writeにする。
- compatibility migrationとstrict schema migrationのverdictをverificationで分離する。

## Three-way Inventory

以下はB consumer snapshot、U consumer projection、P tracked treeのunionを分類したexhaustive resolutionである。`starter/**`はrootへ正規化し、project-only pathは明示したgroupで全件`keep`とする。

### Apply: upstream modified / project upstream-owned unmodified

- Skills: `.agents/skills/{docs-cleanup,post-implementation,qa-prep}/SKILL.md`と`.claude/skills/`の同3 path。
- Agent config: `.claude/settings.json`、`.codex/hooks.json`。
- Guide / standards: `_docs/documentation_guide.md`、`_docs/standards/{documentation_guidelines,documentation_operations}.md`。
- Agent workflow evals: `_evals/agent-workflows/cases/{historical-prompt-not-operational,intentional-omission-risk,malformed-todo-heading,qa-status-verdict-mismatch}.md`、`_evals/agent-workflows/expected-invariants.md`。
- Validator runner / provenance example: `scripts/check-docs.sh`、`docs-template.lock.example.json`。

### Apply: upstream added

- `deno.json`。
- Frontmatter fixtures: `_evals/validator-fixtures/frontmatter/invalid/{duplicate-field,intent-schema-on-qa,qa-schema-on-intent,unknown-field,wrong-type}.md`と`_evals/validator-fixtures/frontmatter/valid/{intent-schema,qa-schema}.md`。
- TypeScript workflow scripts: `scripts/{agent-workflow-hook,scope,test-agent-workflow-hook,test-agent-workflow-smoke,test-validators,validate-doc-links,validate-frontmatter,validate-intent,validate-qa,validate-todo}.ts`。

### Merge: upstream modified / project customized shared

- Root docs: `README.md`はproject product documentationをkeepし、workflow commandに必要な変更だけmergeする。`QUICKSTART.md`はproject onboardingをkeepし、hook script pathとtemplate migration guidanceをmergeする。`AGENTS.md`と`TODO.md`はproject customizationをkeepし、このmigration taskだけproject側で追加する。
- Fixture guide: `_evals/validator-fixtures/README.md`はP固有のknown / unknown schema-marker fixturesとUのinvalid / valid frontmatter matrixを併記する。
- QA fixtures: `_evals/validator-fixtures/qa/invalid/{missing-invariant,qa-archive-path,status-verdict-mismatch,v2-missing-decision-scope,verification-in-progress-status,verification-missing-test-plan-reference}.md`と`_evals/validator-fixtures/qa/valid/{test-plan,verification-pass}.md`は、Pのcanonical referencesとUのfrontmatter契約を両立させる。
- Script migration: PでBから変化した`scripts/{agent-workflow-hook,test-agent-workflow-hook,test-validators,validate-frontmatter}.mjs`の意味差分を、対応するUの`.ts`へmergeする。

### Keep: unchanged shared paths

- byte-identical skill pairs: `docs-inventory`、`docs-prep`、`docs-template-migration`、`implementation-prep`、`qa-review`、`test-maintenance`。
- Root / standards: `CLAUDE.md`、`LICENSE.txt`、`.markdownlint.jsonc`、`_docs/standards/{quality_assurance,security_for_agents}.md`、`_docs/standards/templates/**`、各categoryの`.gitkeep`。
- Unchanged eval fixtures and cases: B / Uで同一の`_evals/agent-workflows/**`および`_evals/validator-fixtures/{intent,links,todo}/**`はP状態をkeepする。
- `scripts/create-template-archive.sh`はbyte-identicalのためkeepする。
- `.github/workflows/docs-ci.yml`はUでmodifiedだが、deltaが未初期化template専用の`starter/**/*.md` globと`starter-expansion` jobだけである。初期化済みdownstreamでは現行lint jobと`./scripts/check-docs.sh`が正しいためPをkeepする。

### Keep absent: upstream removed or template self-meta

- `_docs/{intent,plan,qa}/Workflow/lifecycle-self-audit/**`はPですでに不在であり、Uでもremovedのため不在をkeepする。
- U template rootのrouter `AGENTS.md` / `CLAUDE.md`と`starter/` directory自体はdownstreamへ導入しない。`starter/`内のconsumer filesだけをrootへ投影する。

### Remove: explicitly authorized old `.mjs` files

対応するU `.ts`版の導入・compatibility確認後、次の10 pathだけを削除する。ほかのpathは削除しない。

1. `scripts/agent-workflow-hook.mjs`
2. `scripts/scope.mjs`
3. `scripts/test-agent-workflow-hook.mjs`
4. `scripts/test-agent-workflow-smoke.mjs`
5. `scripts/test-validators.mjs`
6. `scripts/validate-doc-links.mjs`
7. `scripts/validate-frontmatter.mjs`
8. `scripts/validate-intent.mjs`
9. `scripts/validate-qa.mjs`
10. `scripts/validate-todo.mjs`

### Keep: project-only paths

- Runtime / packaging: `.gitignore`、`config.example.toml`、`pyproject.toml`、`uv.lock`、`packaging/systemd/codex-discord-rpc.service.in`、`scripts/install-user-service.sh`、`src/codex_discord_rpc/{__init__,cli,config,git_info,phases,presence,project_detection,rpc,state}.py`、`tests/{test_cli,test_config,test_git_info,test_presence,test_project_detection,test_rpc,test_service,test_state}.py`。
- Core docs: `_docs/archives/plan/Core/codex-rich-presence/plan.md`、`_docs/guide/Core/codex-rich-presence/usage.md`、`_docs/intent/Core/codex-rich-presence/decision.md`、`_docs/qa/Core/codex-rich-presence/{test-plan,verification}.md`。
- Prior migration evidence: `_docs/archives/plan/Workflow/docs-template-v1-migration/plan.md`、`_docs/intent/Workflow/docs-template-v1-migration/decision.md`、`_docs/qa/Workflow/docs-template-v1-migration/{test-plan,verification}.md`、`docs-template.lock.json`。
- Project frontmatter compatibility fixtures: `_evals/validator-fixtures/frontmatter/known/{intent-schema,qa-schema}.md`と`_evals/validator-fixtures/frontmatter/unknown/future-schema.md`。

### Migration-created artifacts

- `TODO.md`の`Workflow-Chore-13`。
- `_docs/archives/plan/Workflow/docs-template-v1-2-migration/plan.md`。
- `_docs/intent/Workflow/docs-template-v1-2-migration/decision.md`。
- `_docs/qa/Workflow/docs-template-v1-2-migration/{test-plan,verification}.md`。

## Tasks

1. New Plan / Intent / QAとTODO taskを現行validatorで検証する。
2. UのTypeScript validator / fixtures / `deno.json` / runnerを導入する。
3. imported scriptsをreviewし、standards等のsemantic schema edit前にexisting project docsへのcompatibility gateを通す。
4. paired skills、hooks、CI、standards、root guidance、fixture customizationをpath-by-pathでmergeする。
5. authorized `.mjs`だけを削除し、compatibility gateを再実行する。
6. compatibility PASS後にlockをUへ進める。
7. qa-review、docs cleanup判断、project regression、diff / provenance reviewを行う。

## QA Plan

- Risk: High（migration、CI、validator、agent workflow、file removal）。
- QA: `_docs/qa/Workflow/docs-template-v1-2-migration/test-plan.md`。
- Agent misbehavior: moving branch混入、root router誤導入、blind replacement、premature lock、bulk schema edit、削除範囲逸脱を確認する。
- Rollback: commit前のactive treeであり、変更はgit diffで復元可能。削除対象はB / P / Uから再取得可能だが、実際のrollback操作はowner指示なしに行わない。

## Deployment / Rollout

active tree内でmigrationと検証を完了する。commit、push、live user service操作は行わない。最終verificationでcompatibility / strict schemaを別判定し、PASSでない場合はlockを進めない。
