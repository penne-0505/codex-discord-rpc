---
title: "Intent: Docs-driven template release migration"
status: active
draft_status: n/a
intent_schema: 2
created_at: 2026-07-22
updated_at: 2026-07-22
references:
  - "_docs/archives/plan/Workflow/docs-template-v1-migration/plan.md"
  - "_docs/qa/Workflow/docs-template-v1-migration/test-plan.md"
related_issues: []
related_prs: []
---

# Intent: Docs-driven template release migration

## Context

このprojectはv1.0.0以前のtemplate commitを採用しているが、採用revisionのlockを持たない。upstreamにはvalidator、why-first schema、paired skills、hooks、provenance運用が追加される一方、project側にはDiscord runtime、service運用文書、root guidanceのcustomizationがある。

## Decisions

### DEC-001: Release provenanceをfull SHAで固定する

- **What**: B、tag付きU、project cutoff Pを固定したthree-way migrationを行い、compatibility PASS後にUを`docs-template.lock.json`へ記録する。
- **Why**: moving branch tipやtag名だけでは、どのupstream contentをproject baselineにしたか再現できず、次回migrationでproject customizationとupstream deltaを分離できないため。
- **Change freedom**: inventoryの表現形式や作業worktreeは変更できるが、B / U / PのidentityとUのtag/full SHA対応は再現可能でなければならない。
- **Why not**: upstream `main`のwholesale copyは、revision driftとproject customization消失を同時に招くため採らない。

### DEC-002: Project customizationをpath ownershipに沿って保全する

- **What**: shared pathはB / U / Pを照合してmergeし、project-only runtime、service installer、systemd unit、project docs、commandを保持する。
- **Why**: template updateはworkflow baselineの更新であり、Discord RPCの実行契約や運用証跡を変更する権限を含まないため。
- **Change freedom**: workflow説明の配置や表現はUの正典に合わせて変更できるが、projectのruntime behavior、privacy boundary、運用手順は維持する。

### DEC-003: Schema adoptionはsemantic editに限定する

- **What**: schema v2対応validatorをlegacy-compatible modeで導入し、新規migration docsはv2にする。既存Core intent / QAは意味を変更しないためlegacy schemaのまま保持する。
- **Why**: marker追加だけのbulk conversionは、既存decisionをwhy-firstへ再構成したという誤った保証を作り、履歴証拠を不要に書き換えるため。
- **Change freedom**: 既存docへsemanticなdecision / QA契約変更を行う将来タスクでは、そのdocをv2へ移行できる。
- **Revisit when**: projectの既存decisionを意味から再設計するタスクが承認されたとき。

### DEC-004: Hooksをguardrailとして導入する

- **What**: UのCodex / Claude lifecycle hook設定とshared scriptを導入し、docs workflowのreminder、write audit、destructive operation guard、closure checkに使う。
- **Why**: skillや規約は自動実行されず、session再開やmulti-file writeで必要なworkflow gateが抜ける可能性があるため。
- **Change freedom**: hook eventやmessageは、同じsafety outcomeとnon-mutating boundaryを保つ限り変更できる。
- **Why not**: hookによるdocs自動更新は、owner authorityとQA evidenceを迂回するため採らない。

### DEC-005: Template self-metaをproject guidanceへ混入させない

- **What**: Uのlifecycle-self-audit plan / intent / QAは導入せず、Bと一致してUでobsoleteになったtemplate workflow記録はcanonical standardsへ吸収後に除く。
- **Why**: template自身の作業履歴がdownstream projectのactive decisionに見えると、project固有記録と配布物の規約を誤読するため。
- **Change freedom**: templateの一般規則、fixture、skill、hookは導入できる。project自身のmigration intent / QAはproject recordとして保持する。

## Consequences / Impact

- 次回template updateはv1.0.0 lockをBとして開始できる。
- 新規docsはwhy-first schema v2を使い、既存legacy docsはsemantic edit時に個別移行する。
- agent lifecycle hookが有効なclientではworkflow guardが追加されるが、Python runtimeとuser service behaviorは変わらない。
- template self-meta recordsはproject treeに残らない。

## Quality Implications

- inventory completenessとlock identityを機械確認する。
- paired skill equality、hook tests、validator fixtures、smoke、markdownlint、project regressionを実行する。
- diff reviewでsource/runtime path不変、project docs保全、branch mixing不在、lock write順を確認する。

## Intent-derived Invariants

- INV-001 (from DEC-001): `docs-template.lock.json`はtag `v1.0.0`とfull SHA `f71e9ab20466ea2972158334261f5ae2b2265754`の組を記録する。
- INV-002 (from DEC-002): `src/**`、`scripts/install-user-service.sh`、`packaging/systemd/**`とCoreのguide / intent / QAにmigration由来の変更を入れない。
- INV-003 (from DEC-003): semantic changeを受けないexisting Core intent / QAへschema markerやDEC再構成を一斉適用しない。
- INV-004 (from DEC-005): Uのlifecycle-self-audit docsとobsolete template workflow recordsをactive project docsとして残さない。

## Rollback / Follow-ups

commitを採用しない場合、active checkoutとlive serviceに影響はない。follow-upはcompatibilityまたはstrict schema判定が非PASSになった場合だけTODOへ追加する。
