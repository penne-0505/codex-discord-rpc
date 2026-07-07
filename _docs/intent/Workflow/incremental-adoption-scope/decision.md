---
title: Incremental adoption scope decision
status: active
draft_status: n/a
created_at: 2026-06-15
updated_at: 2026-06-15
references:
  - "_docs/plan/Workflow/incremental-adoption-scope/plan.md"
  - "_docs/qa/Workflow/incremental-adoption-scope/test-plan.md"
related_issues: []
related_prs: []
---

# Incremental adoption scope decision

## Context

このテンプレートの docs validator (`validate-frontmatter`, `validate-doc-links`, `validate-qa`) は、`_docs/**` や `_evals/**` をファイルシステムごと走査して判定する。新規プロジェクトには適切だが、既存プロジェクトへ後付け導入すると、テンプレート規約に従っていない大量の既存 docs が一斉に検証対象となり、CI が大量のエラーで埋まる。これが「適用が難しくなりすぎる」障壁になっている。

導入の障壁は既存 docs コーパスの量であり、運用台帳である `TODO.md` ではない。`TODO.md` は導入時点で新規採用される運用面であり、検証しても重荷にならない。

## Decision

- 「導入以降に追加された docs」だけを判定対象に絞れる opt-in スコープ機構を追加する。既定は従来通り全走査とし、後方互換を壊さない。
- スコープの母集合決定を新規モジュール `scripts/scope.mjs` に集約し、各 validator はそれを共有する。母集合決定が validator ごとに分散している現状を、この 1 箇所へ寄せる。
- 「導入以降」の定義は git baseline ref からの `--diff-filter=A`（追加されたファイルのみ）とする。一度導入後に既存ファイルを編集してもスコープには入れない。
- 環境変数で制御する: `DD_SCOPE_BASE`（git ref）。テスト・CI 自前計算向けに `DD_SCOPE_PATHS`（明示パスリスト）も受ける。いずれも未設定なら全走査。
- 横断的整合チェック（リンク存在、front-matter references 存在、archive / qa 不変量）は、判定の起点となるファイルだけをスコープで絞り、参照先の存在確認はファイルシステム全体に対して行う。これにより新規 doc から既存 doc へのリンクは壊れず、既存 doc 自体は判定されない。
- `validate-todo.mjs` はスコープの影響を受けず、常に `TODO.md` 全体を検証する。運用台帳は導入時点から管理対象とする。
- env / run 権限が無い場合、スコープ解決は安全側（scope = null = 全走査）へフォールバックし、検証の取りこぼしを生まない。

## Alternatives

- front-matter の `created_at >= 導入日` や `dd_managed: true` マーカーで判定する: 既存 docs に追記が必要で、front-matter の無い既存 docs を機械判定できないため採用しない。
- 管理対象を特定ディレクトリ配下に限定する: 既存プロジェクトのディレクトリ構造と衝突しやすく、移行コストが高いため採用しない。
- `--diff-filter=ACMR`（変更も含む）にする: 「既存 docs を軽く編集しただけで検証対象化され CI が赤くなる」挙動を避けるため、追加のみ (`A`) を既定とする。変更も対象化したい運用は `DD_SCOPE_PATHS` で自前計算できる余地を残す。
- TODO.md もスコープ対象にする: 既存 TODO.md を持つプロジェクトで台帳検証が丸ごと無効化され、運用の中心が無検証になるため採用しない。

## Rationale

スコープ機構を opt-in かつ default-off にすることで、テンプレート自身の CI は従来通り全 docs を dogfooding でき、導入先プロジェクトだけが段階導入を選べる。母集合決定を `scope.mjs` に集約することで、5 箇所に分散していた対象決定の一貫性を担保し、スコープ挙動を 1 箇所で検証できる。

フォールバックを「全走査（more checking）」側に倒すのは、スコープ機構の故障が「検証の取りこぼし（under-checking）」ではなく「過剰検証（over-checking）」として現れるようにするため。安全側の故障モードを選ぶ。

## Consequences / Impact

- 既存プロジェクトは既存 docs に一切手を入れずに、導入以降の docs だけを段階的に品質ゲートへ載せられる。
- validator 実行に `--allow-env`（env 読み取り）と、git ベース時は `--allow-run=git` の権限が追加で必要になる。テンプレート自身の CI は env 未設定なので挙動は変わらない。
- git baseline 方式は CI で baseline commit が fetch されている必要がある（`actions/checkout` の `fetch-depth: 0`）。
- スコープの判定は人間 / agent が baseline ref を正しく設定することに依存する。誤った ref はスコープ集合を誤らせるが、フォールバックと default-off により取りこぼしには倒れない。

## Quality Implications

- default-off により後方互換を保ち、テンプレート自身の docs 検証は全走査のまま維持する。
- 横断チェックの「起点のみ絞る / 参照先は全体」方針により、リンク整合性の意味を壊さない。
- Agent workflow / validator / CI 変更として、agent が「スコープ＝検証を弱める」と誤解し、テンプレート本体の検証まで絞ってしまわないことを agent misbehavior checks で確認する。

## Intent-derived Invariants

- INV-001: `DD_SCOPE_BASE` と `DD_SCOPE_PATHS` が未設定のとき、各 validator は従来通り全 docs を走査する（default-off / 後方互換）。
- INV-002: スコープ有効時、判定対象は「導入以降に追加されたファイル（`--diff-filter=A` 相当）」のみで、既存ファイルは判定されない。
- INV-003: 横断的整合チェックは起点ファイルをスコープで絞っても、参照先の存在確認はファイルシステム全体に対して行う。
- INV-004: `TODO.md` の検証はスコープ設定の有無に関わらず、常に全タスクを対象とする。
- INV-005: スコープの母集合決定は `scripts/scope.mjs` に集約され、frontmatter / doc-links / qa validator はそれを共有する。
- INV-006: env / run 権限が無い場合、スコープ解決は scope = null（全走査）へフォールバックし、検証を取りこぼさない。

## Rollback / Follow-ups

- スコープ機構に問題が出た場合、`DD_SCOPE_BASE` / `DD_SCOPE_PATHS` を未設定に戻すだけで全走査の従来挙動へ復帰できる（コード変更不要）。
- 将来「変更も対象化」が必要になれば、`--diff-filter` の選択肢を env で切り替えられるよう拡張する余地がある。
