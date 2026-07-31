---
title: "Intent: Docs-driven template v1.2.0 migration"
status: active
draft_status: n/a
intent_schema: 2
created_at: 2026-08-01
updated_at: 2026-08-01
references:
  - "_docs/archives/plan/Workflow/docs-template-v1-2-migration/plan.md"
  - "_docs/qa/Workflow/docs-template-v1-2-migration/test-plan.md"
related_issues: []
related_prs: []
---

# Intent: Docs-driven template v1.2.0 migration

## Context

このprojectはdocs-driven template v1.0.0をfull SHA付きlockで採用している。v1.2.0ではvalidatorのTypeScript移行、frontmatter validation強化、workflow-sensitive writeへのRisk通知、template自身とconsumer-facing filesを分離する`starter/`構造が導入された。一方、project側にはproduct README、systemd運用、privacy boundary、Core intent / QA、v1.0.0 migration evidenceがあるため、upstream treeの単純なcopyではproject guidanceとtemplate self-metaが混在する。

## Decisions

### DEC-001: Tagとpeeled full SHAをprovenance contractにする

- **What**: B、U、Pを固定したthree-way migrationを行い、compatibility PASS後にU=`v1.2.0` / `a7fb411edb8974d0c4418fc675edc829c7600728`をlockへ記録する。
- **Why**: annotated tag object、tag名、moving branch tipだけでは実際に統合したcommitを一意に再現できず、次回のupstream deltaとproject customizationを分離できないため。
- **Change freedom**: inventoryやverificationの表現、active tree / worktreeの選択は変えられるが、source、tag object、peeled commit、cutoff manifestの対応は再現可能でなければならない。
- **Why not**: upstream `main`のtipだけを記録する方法は、同じmigrationを後から再構成できないため採らない。

### DEC-002: `starter/`をconsumer projectionとして解釈する

- **What**: Uの`starter/<path>`をdownstream rootの`<path>`へ投影し、template開発用root router、`starter/` directory、`starter-expansion` CI jobは導入しない。shared customized pathはB / U / Pでmergeする。
- **Why**: v1.2.0のroot routerはtemplate repository自身を開発するagent向けであり、初期化済みdownstream projectへ導入するとproject rulesを無効化し、template self-metaを作業規約として誤読させるため。
- **Change freedom**: consumer projectionを実装するcopy / patch方法は変更できる。project固有commands、privacy boundary、runtime / service contractが保全され、template-development routerがactive guidanceにならないことを満たせばよい。
- **Why not**: U root treeのwholesale replacementは、`AGENTS.md`とproduct docsをtemplate開発用内容へ戻すため採らない。

### DEC-003: `.mjs`削除はsemantic portと明示許可の両方を条件にする

- **What**: Uの`.ts`版へP固有の意味差分を移し、new runnerによるcompatibility確認後に、ownerが明示許可した旧`.mjs` 10 pathだけを削除する。
- **Why**: extension renameをblind copyするとdownstreamで追加したfixtureやguardrailを失い、逆に旧版を残すとobsolete validator / hookが誤って実行される二重系になるため。
- **Change freedom**: TypeScriptの型表現やmodule構造はUの実装へ合わせられる。P固有の期待結果とsafety outcomeが保持され、旧entrypointが残らなければよい。
- **Why not**: 旧`.mjs`を互換shimとして残す方法は、documented commandと実行実体が分岐し、次回migrationでbaselineを曖昧にするため採らない。

### DEC-004: Compatibilityとstrict schemaを別gateにする

- **What**: imported validatorをexisting docsへ先に適用してlegacy compatibilityを確認し、新規migration docsはschema v2で作成する。既存live docsのsemantic bulk conversionは行わない。
- **Why**: schema marker追加だけではdecision rationaleを再構成したことにならず、migration regressionと既存document debtの原因を混同するため。
- **Change freedom**: semantic editが必要な既存documentは個別にschema v2へ移行できる。今回変更しないdocumentのschemaはlegacy-compatible validatorが受理すればよい。
- **Revisit when**: existing Core decisionまたはQA contractを意味から変更する承認済みタスクが開始されたとき。

### DEC-005: Template self-metaとproject evidenceを分離する

- **What**: upstreamのtemplate-development router、`starter/` directory、lifecycle-self-audit recordはactive project treeへ導入せず、project自身のprior/current migration intentとverificationを保持する。
- **Why**: template自身の作業履歴がdownstreamのactive decisionに見えると、どのcontractがCodex Discord RPCに適用されるか判別できなくなるため。
- **Change freedom**: general-purpose standards、fixtures、skills、hooksはproject workflowとして導入できる。project migration evidenceのpathや文言はcanonical linkを保つ限り変更できる。

### DEC-006: Workflow-sensitive riskをwrite時に通知し、分類は作業者に残す

- **What**: CI、standards、agent config、workflow scriptへのwriteではRisk High文書chainの候補を事前通知し、Stopではworking-tree上のintent / QA evidenceを確認する。ただしhookはRiskを自動確定しない。
- **Why**: workflow変更の文書要件を完了時だけ検出すると、設計判断とQAを後付けすることになる一方、pathだけでRiskを確定すると実際の変更内容を無視した過剰拘束になるため。
- **Change freedom**: workflow-sensitive path集合、通知文、hook eventは、実装前通知、working-tree evidence、human/agent judgementの境界を保つ限り変更できる。
- **Why not**: hookがRiskやscopeを自動決定する方式は、変更の意味とowner authorityをpath matchへ委譲するため採らない。

## Consequences / Impact

- 次回template updateはv1.2.0をBとして開始できる。
- Validator / hook commandは`.ts`へ統一され、旧`.mjs` entrypointは残らない。
- Agent clientはworkflow-sensitive writeをRisk High候補として事前通知できるが、Risk確定やdocs自動更新は行わない。
- Product runtime、Discord表示情報、service lifecycle、privacy contractは変わらない。
- Existing Core intent / QAはsemantic changeがないため一斉schema変換されない。
- Workflow-sensitive writeは文書要件候補を早期に通知されるが、hookがRiskやscopeを自動決定しない。

## Quality Implications

- tag objectとpeeled SHA、remote branch containment、lock write順をstatic reviewする。
- `.mjs`→`.ts`のsemantic comparison、hook unit / smoke、validator fixtures、paired skills、markdownlintを実行する。
- source / service / Core docsのcutoff blobとfinal blobを比較する。
- 削除path集合が許可済み10件と一致し、ほかのdeletionがないことをdiffで確認する。

## Intent-derived Invariants

- INV-001 (from DEC-001): migration完了時の`docs-template.lock.json`はtag `v1.2.0`とpeeled full SHA `a7fb411edb8974d0c4418fc675edc829c7600728`の組を記録する。
- INV-002 (from DEC-002): `src/**`、`scripts/install-user-service.sh`、`packaging/systemd/**`、Core guide / intent / QA、`AGENTS.md`のproject固有command / privacy boundaryをmigrationで失わない。
- INV-003 (from DEC-003): deleted path集合は許可済み旧`.mjs` 10件と一致し、それ以外のdeleted pathを含まない。
- INV-004 (from DEC-004): semantic changeを受けないexisting Core intent / QAへmigration由来のbulk schema conversionを行わない。
- INV-005 (from DEC-005): template root router、`starter/` directory、lifecycle-self-audit docsをactive project guidanceとして残さない。

## Rollback / Follow-ups

compatibility PASS前はlockを変更しない。未解決のmerge、unauthorized deletion、strict schema failureがあればmigrationを完了扱いにせず、TODOとverificationへ残す。rollbackの実行はowner指示なしに行わない。
