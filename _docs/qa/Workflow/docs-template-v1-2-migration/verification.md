---
title: "QA Verification: Docs-driven template v1.2.0 migration"
status: active
draft_status: n/a
qa_schema: 2
qa_status: verified
risk: High
created_at: 2026-08-01
updated_at: 2026-08-01
references:
  - "_docs/archives/plan/Workflow/docs-template-v1-2-migration/plan.md"
  - "_docs/intent/Workflow/docs-template-v1-2-migration/decision.md"
  - "_docs/qa/Workflow/docs-template-v1-2-migration/test-plan.md"
related_issues: []
related_prs: []
---

# QA Verification: Docs-driven template v1.2.0 migration

## Summary

clean cutoff P=`598418795d684b014b660f9c78842705e1856aa5`で、B=`v1.0.0` / `f71e9ab20466ea2972158334261f5ae2b2265754`からU=`v1.2.0` / `a7fb411edb8974d0c4418fc675edc829c7600728`へthree-way migrationを実施した。Uのconsumer-facing `starter/`内容だけをproject rootへ投影し、template開発用router、`starter-expansion` CI、self-metaを除外した。

Compatibility migration: PASS。TypeScript validatorをstandards semantic edit前のexisting project docsへ適用した第一gate、skills / hooks / standards / fixturesと許可済み`.mjs`削除後の第二gate、lock更新後のclosure gateがすべてPASSした。

Strict schema migration: scoped PASS。新規migration intent / QAはschema v2で検証し、frontmatter unknown-field / cross-kind markerをstrictに拒否した。semantic changeのないexisting Core intent / QAはcutoff blobを保持し、理由のないbulk schema conversionを行っていない。

## Verification Verdict

Verdict: PASS

## Commands Run

```bash
date '+%Y-%m-%d %H:%M:%S %Z'
git status --short --branch
git rev-parse HEAD
git ls-remote --tags https://github.com/penne-0505/docs_driven_dev_template.git
git ls-remote --heads https://github.com/penne-0505/docs_driven_dev_template.git
gh api repos/penne-0505/docs_driven_dev_template/releases?per_page=100
./scripts/check-docs.sh
deno fmt --check scripts/*.ts
deno check scripts/*.ts
deno lint scripts/*.ts
deno run --allow-read --allow-write --allow-env --allow-run scripts/test-validators.ts
deno run --allow-read --allow-write --allow-env --allow-run scripts/test-agent-workflow-hook.ts
deno run --allow-read scripts/test-agent-workflow-smoke.ts
npx --yes markdownlint-cli2 "_docs/**/*.md" "_evals/**/*.md" "README.md" "AGENTS.md" "TODO.md" "QUICKSTART.md" "!_docs/archives/**/*" "!_docs/standards/templates/**/*" --config .markdownlint.jsonc
uv sync --extra dev
uv run ruff check .
uv run pytest
uv run python -m compileall -q src tests
uv build --out-dir /tmp/codex-discord-rpc-v1-2-build.YJTZLs
uv run codex-discord-rpc render --repo .
uv run codex-discord-rpc doctor
bash -n scripts/install-user-service.sh
./scripts/install-user-service.sh --dry-run
git diff --check
git diff --cached --check
```

## Automated Test Results

| Command / Test | Result | Notes |
| --- | --- | --- |
| Baseline `./scripts/check-docs.sh` | PASS | migration write前の旧`.mjs` validator / hook / fixtureがPASS。 |
| TypeScript compatibility gate 1 | PASS | 7 imported validator filesをformat / typecheckし、unchanged existing docsと全validator fixtureがPASS。 |
| Final `./scripts/check-docs.sh` | PASS | 10 TypeScript files、validator fixtures、hook unit / smoke、paired-skill assertionsがPASS。High Risk Verification warningはverification作成前だけに限定。 |
| `deno lint scripts/*.ts` | PASS | 10 files checked。 |
| Markdownlint | PASS | 68 files、0 issue。 |
| Paired skill comparison | PASS | `.agents` / `.claude`の9 skill pairがbyte-identical。 |
| Frontmatter strict fixtures | PASS | valid / known schema markerを受理し、duplicate、unknown、wrong type、cross-kind markerを拒否。 |
| Hook unit / smoke | PASS | Risk通知、Risk非確定、working-tree evidence、destructive guard、permission contractを確認。 |
| Changed-path inventory audit | PASS | final changed path 65件、B/U/P unionまたはmigration-created artifactに未分類0。 |
| Deletion allowlist audit | PASS | deleted pathは明示許可済み旧`.mjs` 10件と完全一致、extra 0。 |
| `uv run ruff check .` | PASS | lint errorなし。 |
| `uv run pytest` | PASS | 41 tests passed in 0.23s。 |
| `compileall` | PASS | `src` / `tests` syntax compilation成功。 |
| `uv build` | PASS | sdistとwheelをtemporary outputへbuild。 |
| CLI render / doctor | PASS | static payload生成とruntime diagnosticsが成功。secret値は出力していない。 |
| Installer dry-run | PASS | checkout-bound unit設定を表示し、live stateを変更せず終了。 |
| Tag / lock review | PASS | remote `v1.2.0^{}`とlock commitが`a7fb411edb8974d0c4418fc675edc829c7600728`で一致。 |
| Diff checks | PASS | staged / unstagedともwhitespace errorなし。 |

`jq`はhostに未導入、`deno eval --allow-read`はこのDeno版で非対応だったため、pre-lock JSON確認はfixed-schema exact matchへ切り替えた。lock更新後はremote tag resolution、exact tag / SHA、full docs wrapperで再確認した。

## Manual QA Results

| Checklist Item | Result | Notes |
| --- | --- | --- |
| Project root guidance | PASS | `AGENTS.md`、README、Docs CIはcutoffから変更せず、Quickstartはhook path / permissionだけを更新。 |
| Runtime / service preservation | PASS | `src/**`、installer、systemd unit、Core guide / intent / QAのdiffは空。 |
| Consumer projection | PASS | `starter/`とtemplate root routerを導入せず、consumer settings / skillsだけをrootへ反映。 |
| CI self-meta exclusion | PASS | `starter/**/*.md` globと`starter-expansion` jobを初期化済みdownstreamへ導入していない。 |
| Imported script safety | PASS | remote import、network送信、credential読取、docs自動更新なし。git statusとtemporary test fixtureだけを扱う。 |
| Hook judgement boundary | PASS | workflow-sensitive pathでRisk High候補を通知するが、Risk / scopeを自動確定しない。 |
| Project fixture preservation | PASS | prior `known/` / `unknown/` frontmatter fixturesを削除せず、新strict contractのvalid / invalid coverageへ接続。 |
| Lock sequencing | PASS | pre-lock compatibility / regression PASS後にlockを更新し、更新後にtagとwrapperを再検証。 |

## Acceptance Criteria Coverage

| ID | Result | Evidence |
| --- | --- | --- |
| AC-001 | PASS | PlanにB / U tag object / peeled commit、P、cutoff、remote branch containmentを記録。 |
| AC-002 | PASS | three-way inventoryとfinal changed-path 65件の集合監査でunclassified 0。 |
| AC-003 | PASS | `starter/`、template router、lifecycle-self-audit、starter CI jobが不在。 |
| AC-004 | PASS | validators、fixtures、skills、hooks、standardsを統合し、root / Core customizationを保持。 |
| AC-005 | PASS | P固有hook anchorsとfrontmatter fixturesを`.ts`へ移し、deleted集合は許可済み10件だけ。 |
| AC-006 | PASS | compatibility PASSとstrict schema scoped PASSを分離し、Core docsをbulk conversionしていない。 |
| AC-007 | PASS | final wrapper、Deno lint/typecheck、fixtures、hooks、paired skills、markdownlintがPASS。 |
| AC-008 | PASS | runtime diff 0、Ruff / pytest 41 / compile / build / CLI / doctor / installer dry-runがPASS。 |
| AC-009 | PASS | compatibility後にlockをv1.2.0 exact pairへ進め、remote tagと再照合。 |

## Decision Conformance

| ID | Result | Why the implementation remains aligned |
| --- | --- | --- |
| DEC-001 | PASS | annotated tagをpeeled full SHAへ解決し、moving tipをlockに使っていない。 |
| DEC-002 | PASS | `starter/`をconsumer projectionとして解釈し、project root / runtimeをwholesale replacementしていない。 |
| DEC-003 | PASS | P固有semantic deltaを`.ts`へ移し、compatibility確認後にowner許可済み10 pathだけを削除。 |
| DEC-004 | PASS | imported validatorsをexisting docsへ先行適用し、新規docsだけschema v2、Core blobsは不変。 |
| DEC-005 | PASS | template self-metaを除外し、prior/current project migration evidenceを保持。 |
| DEC-006 | PASS | hook testsでwrite-time notice、working-tree evidence、Risk非確定境界を確認。 |

## Invariant Coverage

| ID | Result | Evidence |
| --- | --- | --- |
| INV-001 | PASS | lockは`v1.2.0` / `a7fb411edb8974d0c4418fc675edc829c7600728`。 |
| INV-002 | PASS | runtime、service、Core docs、AGENTS、README、Docs CIのcutoff diffは空。 |
| INV-003 | PASS | deleted path集合は許可済み旧`.mjs` 10件、extra 0。 |
| INV-004 | PASS | existing Core intent / QAのcutoff blobを保持。 |
| INV-005 | PASS | template router、`starter/`、lifecycle-self-audit docsが不在。 |

## Deferred / Not Covered

| ID | Reason | Follow-up |
| --- | --- | --- |
| Remote GitHub Actions | push / PRは依頼scope外であり、local Docs CI相当を実行した。 | commit / push時に通常のDocs CIで再確認。 |
| Live Discord / systemd restart | runtime、installer、unitに変更がなく、live stateを乱さない境界。 | None。 |
| Full existing-doc schema conversion | semantic editのないCore docsへmarkerだけを足すことはDEC-004でscope外。 | 将来のsemantic edit時に対象docを個別移行。 |

## Residual Risks

None

## Follow-up TODOs

None
