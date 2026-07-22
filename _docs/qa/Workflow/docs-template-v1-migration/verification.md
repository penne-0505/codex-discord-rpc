---
title: "QA Verification: Docs-driven template v1.0.0 migration"
status: active
draft_status: n/a
qa_schema: 2
qa_status: verified
risk: High
created_at: 2026-07-22
updated_at: 2026-07-22
references:
  - "_docs/archives/plan/Workflow/docs-template-v1-migration/plan.md"
  - "_docs/intent/Workflow/docs-template-v1-migration/decision.md"
  - "_docs/qa/Workflow/docs-template-v1-migration/test-plan.md"
related_issues: []
related_prs: []
---

# QA Verification: Docs-driven template v1.0.0 migration

## Summary

pre-v1.0.0 projectをlegacy bootstrap手順でv1.0.0へ移行した。`B=e6dc4331a81af21494208610b22ef2d9ecdce885`、`U=v1.0.0/f71e9ab20466ea2972158334261f5ae2b2265754`、clean cutoff `P=fc463525b91dac8e36ab8c817cb8d71c9461889d`を固定し、B→U / B→Pの122 path inventoryに従ってreconcileした。migration自身が作成したPlan / Intent / QA test-plan / verification / lockとfrontmatter fixture 3件の計8 artifactは別ledgerで分類し、最終監査境界を`122 upstream/project inventory + 8 migration-created artifacts`として確認した。

Compatibility migration: PASS。legacy Core docsを変更せず、Uのvalidator、fixture、paired skills、hooks、CI、standardsが通過した。

Strict schema migration: scoped PASS。新規migration intent / QAはschema v2で検証し、semantic changeのないexisting Core intent / QAはupstreamのlegacy compatibility契約に従って一斉変換しなかった。bulk conversionはdeferred acceptance criterionではなくout of scopeである。

## Verification Verdict

Verdict: PASS

## Commands Run

```bash
date --iso-8601=seconds
./scripts/check-docs.sh
git -C /home/penne/dev/tools/templates/docs_driven_dev_template cat-file -t e6dc4331a81af21494208610b22ef2d9ecdce885
git -C /home/penne/dev/tools/templates/docs_driven_dev_template show -s --format='%H %cI %s' e6dc4331a81af21494208610b22ef2d9ecdce885
git -C /home/penne/dev/tools/templates/docs_driven_dev_template rev-parse v1.0.0^{commit}
git -C /home/penne/dev/tools/templates/docs_driven_dev_template show -s --format='%H %cI %s' f71e9ab20466ea2972158334261f5ae2b2265754
git -C /home/penne/dev/tools/templates/docs_driven_dev_template diff --name-status e6dc4331a81af21494208610b22ef2d9ecdce885..f71e9ab20466ea2972158334261f5ae2b2265754
git diff --name-only fc463525b91dac8e36ab8c817cb8d71c9461889d..HEAD
deno fmt --check scripts/*.mjs
deno run --allow-read --allow-write --allow-env --allow-run scripts/test-validators.mjs
deno run --allow-read --allow-run=git scripts/test-agent-workflow-hook.mjs
deno run --allow-read scripts/test-agent-workflow-smoke.mjs
cmp .agents/skills/<skill>/SKILL.md .claude/skills/<skill>/SKILL.md
npx --yes markdownlint-cli2 "_docs/**/*.md" "_evals/**/*.md" "README.md" "AGENTS.md" "TODO.md" "QUICKSTART.md" "!_docs/archives/**/*" "!_docs/standards/templates/**/*"
uv sync --extra dev
uv run ruff check .
uv run pytest
uv run python -m compileall -q src tests
uv build --out-dir /tmp/docs-template-v1-rollout/codex-discord-rpc-dist-review-fix
uv run codex-discord-rpc render --repo .
bash -n scripts/install-user-service.sh
./scripts/install-user-service.sh --dry-run
git diff --check
```

## Automated Test Results

| Command / Test | Result | Notes |
| --- | --- | --- |
| Baseline `./scripts/check-docs.sh` | PASS | migration write前、旧validator 6 files / fixtureがPASS。 |
| Final `./scripts/check-docs.sh` | PASS | 10 Deno files、intent / QA / scope fixture、hook unit / smokeがPASS。 |
| Frontmatter schema marker fixture | PASS | `intent_schema` / `qa_schema`を既知fieldとして受理し、未知`future_schema`はwarningを維持。 |
| P→C classification set audit | PASS | 実変更90 pathを122-path unionまたは8-artifact ledgerへ分類し、unclassified 0。 |
| Deno format | PASS | 10 files checked。 |
| Markdownlint | PASS | 58 files、0 issue。 |
| Paired skill `cmp` | PASS | 9 skill pairsがbyte-identical。 |
| `uv run ruff check .` | PASS | lint errorなし。 |
| `uv run pytest` | PASS | 41 tests passed。 |
| `compileall` | PASS | `src` / `tests` syntax compilation成功。 |
| `uv build` | PASS | sdistとwheelをtemporary outputへbuild。 |
| CLI render | PASS | Discord接続なしでproject payloadを生成。 |
| Installer dry-run | PASS | isolated worktreeのproject / unit / config / CLI pathを表示し、live stateを変更せず終了。 |
| `git diff --check` | PASS | whitespace errorなし。 |

## Manual QA Results

| Checklist Item | Result | Notes |
| --- | --- | --- |
| Project root guidance | PASS | AGENTSのproject command / privacy boundary、README、Quickstartのservice手順を保持。 |
| Runtime / service preservation | PASS | `src/**`、installer、unit、Core guide / intent / QA、READMEのdiffは空。 |
| CI preservation | PASS | existing trigger / markdownlint scopeを保持し、U wrapperを実行。 |
| Template self-meta | PASS | Uのlifecycle-self-audit docsは未導入、Bと一致したobsolete 11 pathだけを除いた。 |
| Hook safety review | PASS | docs自動更新・外部送信なし。destructive command / sensitive path guardとclosure auditをunit test。 |
| Isolation | PASS | active checkout、live service、remoteを操作していない。 |

## Acceptance Criteria Coverage

| ID | Result | Evidence |
| --- | --- | --- |
| AC-001 | PASS | B / U / P、tag/full SHAをPlan、Intent、lockへ記録。 |
| AC-002 | PASS | 122 upstream/project pathを7 resolution groupへ分類し、migration-created 8 artifactを別ledgerへ分類。P→C実変更90 pathの集合監査で未分類0。 |
| AC-003 | PASS | runtime / service / Core recordsのcutoff diffが空、root customizationをmerge。 |
| AC-004 | PASS | validator、fixture、paired skill、hook、CI、standardsの全gate PASS。 |
| AC-005 | PASS | template self-meta 4 pathを未導入。obsolete 11 pathはB blob一致とcanonical authority移行を確認。 |
| AC-006 | PASS | compatibilityとstrict schema結果をSummaryで分離。Core legacy blobは不変。 |
| AC-007 | PASS | docs gate、markdownlint、Ruff、pytest、compileall、buildがPASS。 |
| AC-008 | PASS | runtime/source変更0。compatibility PASS後にlockをUへ作成し再検証。 |
| AC-009 | PASS | local migrationを単一commitにまとめるclosure stepを実施し、pushしない。 |

## Decision Conformance

| ID | Result | Conformance |
| --- | --- | --- |
| DEC-001 | PASS | moving tipを使わずB / tag付きU / clean Pを固定し、lockをcompatibility後に作成。 |
| DEC-002 | PASS | shared pathを三者mergeし、project-only runtimeとservice contractを保持。 |
| DEC-003 | PASS | new docsだけv2、semantic changeのないCore legacy docsはsupported legacyとして保持。 |
| DEC-004 | PASS | hooksはnon-mutating guardrailとして導入し、unit / smokeで契約を確認。 |
| DEC-005 | PASS | template self-metaをactive project guidanceへ混入させず、project migration recordだけを保持。 |

## Invariant Coverage

| ID | Result | Evidence |
| --- | --- | --- |
| INV-001 | PASS | lockのtag `v1.0.0`とcommit `f71e9ab20466ea2972158334261f5ae2b2265754`がtag resolutionと一致。 |
| INV-002 | PASS | `src/**`、installer、unit、Core docsのdiffは空。 |
| INV-003 | PASS | existing Core intent / QAのcutoff blobを保持。 |
| INV-004 | PASS | lifecycle-self-audit 4 pathとobsolete template workflow 11 pathが不在。 |

## Deferred / Not Covered

| ID | Reason | Follow-up |
| --- | --- | --- |
| Live Discord / systemd | runtime / installer / unitに変更がなく、active serviceを乱さないscope boundary。 | None。existing project verificationを保持。 |
| Dedicated typechecker | project dependencies / documented commandsにmypy / pyright等がない。 | None。Ruff、compileall、pytest、buildでnon-live regressionを確認。 |
| Full legacy schema conversion | upstream standardがsemantic edit時の個別移行を要求し、bulk marker追加を禁止する。 | None。次回semantic edit時に対象docをv2へ移行。 |

## Residual Risks

None

## Follow-up TODOs

None.
