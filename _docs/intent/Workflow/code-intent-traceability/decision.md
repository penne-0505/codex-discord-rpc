---
title: Code ↔ intent traceability decision
status: active
draft_status: n/a
created_at: 2026-06-19
updated_at: 2026-06-19
references:
  - "_docs/plan/Workflow/code-intent-traceability/plan.md"
  - "_docs/qa/Workflow/code-intent-traceability/test-plan.md"
  - "_docs/intent/Workflow/intentional-omission-risk/decision.md"
related_issues: []
related_prs: []
---

# Code ↔ intent traceability decision

## Context

intent は why / why not を残すために設けている。自己説明的なコードには限度があり、とくに「なぜそうしなかったか」はコードに痕跡が残らない。

現状、コードから intent へ到達する手がかりがない。タスク起点で入れば「現状のドキュメントを参照してから実装」という号令はあるが、それは「どの intent を見るべきか」のマッピングを供給しない。コード起点（コードを読んでいて「これは何故こうなっているのか」と気づく）では、到達経路が事実上ない。

結果として、将来の作業者や agent が、意図的な省略・非自明な実装の形を「未実装」「不要」と誤認し、設計判断を壊すリスクが残る。これは [intentional omission risk decision](../intentional-omission-risk/decision.md) が docs / PR / commit のレベルで守ろうとしている的と同じであり、本判断はその防御をコード本体まで降ろすものである。

## Decision

- コードが設計判断を体現していて、素朴な読み手が誤って「直す」「消す」をしうる非自明な箇所には、intent への参照をコメントで残す。**ターゲット型**とし、全コード・全コメントへの一律義務化はしない。
- 参照のアンカーは**安定 ID（`INV-xxx` / `AC-xxx`）を主、intent slug を従**にする。
- 書式は grep 可能な接頭辞を用いる。
  - `// intent: INV-003 (Workflow/intentional-omission-risk) — <why / why not の一行>`
  - why not が主旨のときは `// intent why-not: INV-002 (<Area>/<slug>) — <理由>`
- **線引き**: 壊れたら落ちる形でテスト化できる不変条件はテスト（INV 名）に割り当てる。テスト化しにくい why not・意図的省略・構造的選択はコメントに残す。同一条件をテストとコメントで二重義務化しない。
- **intent 側の改善**: Intent-derived Invariants は安定 ID で、コードから一行で引用できる粒度・断定形で書く。任意で、各 INV が「どこで体現・enforce されているか」を示す back-reference を残してよい。
- **強制レベル**: コード参照の有無を validator で error として機械強制しない。「参照が要るほど非自明か」は機械判定できず、強制すればノイズと形骸化を生むため。遵守は skill（implementation-prep / test-maintenance / post-implementation）と review で担保する。

## Alternatives

- **全コードへのコメント参照を義務化する**: validator で機械強制しやすい一方、ノイズと形だけの記述を量産し、[intentional omission risk decision](../intentional-omission-risk/decision.md) の INV-001（小タスクに記録欄を強制しない）と同型の失敗を再生産する。不採用。
- **生 doc パス参照（`// see decision.md`）を正典にする**: 書きやすいが曖昧で、doc が動くと腐る。安定 ID を主にする方が意味的に正確で腐敗耐性も高いため、不採用。
- **intent → code の back-reference のみで賄う**: intent を先に開く前提でしか発火せず、コード起点の「読んでいて気づく」を拾えない。補完としては採用するが、単独解にはしない。
- **テストの INV 名だけで代替する**: コード起点で発火する強い経路だが、不在（why not）を表明しづらい。テストは線引きの片側として併用する。
- **validator で機械強制する**: ターゲット型は非自明性を機械判定できず、誤検出を生む。将来の任意拡張として「参照先 INV/intent の実在確認（リンク切れ検出）」に限定する。

## Rationale

why not はコードに不在として現れ、テストでも git blame でも拾いにくい。常時可視でその不在を説明できる媒体は実質コードコメントだけである。すなわち本判断の動機（why not を残す）と、コメント参照が最も代替不能な領域（不在の説明）が一致している。

対象を「将来、善意で直されそうな非自明箇所」に限定することで、テンプレートの軽量 Fast Track 哲学を壊さずに済む。アンカーを安定 ID に掛けることで、intent を archive しない既存ルールと合わさり、参照は腐りにくくなる。

## Consequences / Impact

- 非自明箇所のコメントが増えるが、対象を限定するためノイズは抑制される。
- standards / intent template / skills（`.claude` と `.agents` の両系）/ AGENTS.md / documentation_guide への波及更新が必要になる。
- 機械強制しないため、遵守は人 / agent の判断と review に依存し、完全な機械保証にはならない。
- 既存の intent-derived invariant 概念および test-maintenance の INV コメント例と接続し、それを拡張する。

## Quality Implications

- コード起点でも why / why not（intent）へ到達できる。
- ターゲット型を維持し、全コード義務化へ滑らない。
- documentation rule / skill の変更として、agent misbehavior checks で「全コード義務化への逸脱」「生パス化」「テストとコメントの二重義務化」「validator での機械強制化」へ戻らないことを確認する。

## Intent-derived Invariants

- INV-001: コード参照ルールはターゲット型であり、全コード・全コメントへ intent 参照を義務化してはならない。
- INV-002: コード参照のアンカーは安定 ID（`INV-xxx` / `AC-xxx`）を主とし、生 doc パスのみの参照を正典にしてはならない。
- INV-003: テストで表明できる不変条件はテストへ、テスト化しにくい why not / 意図的省略はコメントへ割り当て、同一条件をテストとコメントで二重義務化してはならない。
- INV-004: validator はコード参照の有無を error として機械強制してはならない。遵守は skill と review で担保する。
- INV-005: intent 側の Intent-derived Invariants は、安定 ID かつコードから一行で引用できる粒度・断定形で書く。
- INV-006: コード参照書式は grep 可能な接頭辞（`intent:` / `intent why-not:`）を用いる。

## Rollback / Follow-ups

- ノイズが顕在化した場合は、対象を user-visible な省略・互換性判断・意図的な非対応に絞る文言へ狭める。
- Follow-up（別 TODO 候補）: コード → intent 参照のリンク切れ検出 validator（任意・default-off。参照先 INV / intent slug の実在のみを確認し、参照の有無は強制しない）。
- Follow-up（別 TODO 候補）: `_evals/agent-workflows/cases/` に「コード起点で intent に到達できるか」を確認するケースを追加する。
