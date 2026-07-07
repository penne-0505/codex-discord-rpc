---
title: Code ↔ intent traceability plan
status: active
draft_status: n/a
created_at: 2026-06-19
updated_at: 2026-06-19
references:
  - "_docs/intent/Workflow/code-intent-traceability/decision.md"
  - "_docs/qa/Workflow/code-intent-traceability/test-plan.md"
related_issues: []
related_prs: []
---

# Code ↔ intent traceability plan

## Overview

コード起点でも why / why not（intent）へ到達できるよう、設計判断を体現した非自明なコード箇所に intent への参照コメントを残すルールを新設する。アンカーは安定 ID（`INV-xxx` / `AC-xxx`）を主とし、テストで表明できる不変条件はテストへ、テスト化しにくい why not はコメントへ振り分ける。機械強制はせず、standards / intent template / skills / AGENTS / guide に規約として展開する。

## Scope

- `_docs/standards/quality_assurance.md` に「intent ↔ code traceability」節を新設する（正典）。
- `_docs/standards/templates/intent.md` に、INV を安定 ID・一行引用可能な粒度で書く指針と、任意の back-reference 欄を追加する。
- `test-maintenance` / `implementation-prep` / `post-implementation` skill に、コード起点トレーサビリティの手順（参照を残す / 確認する、テストとの線引き）を追加する。
- skill 変更は `.claude/skills/` と `.agents/skills/` の両方へ同期する。
- `AGENTS.md` の原則に code → intent 参照の一行を追加する。
- `_docs/documentation_guide.md` にクイックリファレンスとしてミラーする。
- `TODO.md` に本タスクを起票する（dogfooding）。

## Non-Goals

- 全コード・全コメントへの参照義務化。
- 生 doc パス参照を正典にすること。
- コード参照の有無を validator で機械強制すること。
- 既存ソースコードへの遡及的なコメント付与（テンプレート本体に対象コードはない）。
- リンク切れ検出 validator の実装（任意・別 TODO の follow-up に回す）。
- agent-workflows eval ケースの追加（任意・別 TODO の follow-up に回す）。

## Requirements

- **Functional**:
  - quality_assurance.md がターゲット型・書式・線引き・強制レベルを規定すること。
  - intent template が安定 ID 粒度ガイドと任意 back-reference を含むこと。
  - 3 skill がコード起点トレーサビリティ手順を含み、`.claude` と `.agents` で同期されていること。
  - AGENTS.md と documentation_guide が正典と矛盾しない要約を含むこと。
- **Non-Functional**:
  - 既存の Fast Track 哲学（小タスクへの記録欄を増やさない）を壊さないこと。
  - 既存検証（markdownlint + 全 validator + test-validators）が PASS すること。
  - 規則が intentional-omission-risk decision の INV と矛盾しないこと。

## Tasks

1. quality_assurance.md に traceability 節を追加する。
2. intent template に INV 粒度ガイドと任意 back-reference を追加する。
3. test-maintenance / implementation-prep / post-implementation skill を更新する（`.claude` と `.agents` 両方）。
4. AGENTS.md に原則を一行追加する。
5. documentation_guide にミラーを追加する。
6. 検証コマンド一式を実行し、QA verification を作成して `qa-review` で PASS 可否を確認する。

## QA Plan

- Risk level: Medium
- QA document: `_docs/qa/Workflow/code-intent-traceability/test-plan.md`
- Test strategy:
  - diff review: 正典 / template / skills / AGENTS / guide が規則を一貫して記述すること。
  - sync check: skill が `.claude` と `.agents` で同一であること。
  - validator / static check: markdownlint と全 validator、test-validators の PASS。
  - agent misbehavior check: 規則が全コード義務化 / 生パス化 / 二重義務化 / 機械強制へ逸脱していないこと、intentional-omission-risk の INV と矛盾しないこと。

## Deployment / Rollout

テンプレート repo 内の docs / standards / skills を同時更新する。runtime コードや secret は扱わない。利用先プロジェクトは、更新後の standards と skill に従って新規・改修コードへ参照コメントを残すだけで段階的に適用できる。問題時は standards 節と skill 追記を戻せば従来運用へ復帰する。
