---
title: Intentional omission risk decision
status: active
draft_status: n/a
created_at: 2026-05-30
updated_at: 2026-05-30
references:
  - "_docs/qa/Workflow/intentional-omission-risk/test-plan.md"
related_issues: []
related_prs: []
---

# Intentional omission risk decision

## Context

`Why not` を全タスクで強制すると、小規模変更にも余計な記録欄が増え、形だけの記述が増えやすい。一方で、意図的に実装していない制限・非対応・省略が記録されていないと、将来の作業者や agent が「未実装なので直すべき」と誤認し、元の設計意図を壊す可能性がある。

## Decision

- `Why not` 専用フィールドや validator 強制は追加しない。
- Fast Track でも、将来の作業者が未実装や欠落と誤認しそうな非対応・制限・省略は intentional omission risk として扱う。
- intentional omission risk がある場合は、変更の重さに応じて TODO Description、Plan Non-Goals、Intent Alternatives / Rationale のいずれかへ理由を残す。
- intentional omission risk が設計判断として後続変更に影響する場合は、Size が小さくても docs-prep 対象にできる。

## Alternatives

- `Why not` フィールドを TODO schema に追加する: すべての小規模変更に記録義務が広がり、ノイズが増えるため採用しない。
- validator で `Alternatives` や `Non-Goals` の実質内容を強制する: semantic な記録品質は機械判定しにくく、形だけの記述を誘発するため採用しない。
- 現状維持にする: 中規模以上の変更は守れるが、小さい intentional omission が将来の誤修正を招く穴が残るため採用しない。

## Rationale

判定軸だけを追加すれば、普段の Fast Track は軽いまま保てる。記録対象を「将来、善意で直されそうな不在」に限定することで、Why not の網羅ではなく、将来の誤修正防止に必要な判断だけを拾える。

## Consequences / Impact

- 小規模変更でも、非対応や制限が将来の修正圧を生む場合は軽量な根拠を残す。
- 必須フィールドや validator は増えないため、既存 TODO schema の運用コストはほぼ変わらない。
- 判断は人間または agent のリスク認識に依存するため、完全な機械保証にはしない。

## Quality Implications

- Fast Track は軽量性を維持する。
- 意図的な不在が将来の誤修正を招く場合、少なくとも TODO Description / Plan Non-Goals / Intent Alternatives のどこかで理由を追える。
- Agent workflow / documentation rule の変更として、agent misbehavior checks で古い Fast Track 解釈に戻らないことを確認する。

## Intent-derived Invariants

- INV-001: Fast Track guidance must not require a dedicated `Why not` field or validator-enforced why-not content for every small task.
- INV-002: Fast Track guidance must tell agents to record rationale when an intentional omission could be mistaken for missing work later.
- INV-003: Docs-prep guidance must allow small tasks to escalate to design-decision documentation when intentional omission risk affects future work.
- INV-004: Agent workflow / skill guidance must keep the lightweight record locations explicit: TODO Description, Plan Non-Goals, or Intent Alternatives / Rationale.

## Rollback / Follow-ups

- If this guidance causes noisy documentation, narrow the wording to examples of user-visible limitations, compatibility decisions, and intentionally unsupported behavior.
