---
title: "QA Test Plan: Intentional omission risk"
status: active
draft_status: n/a
qa_status: planned
risk: Medium
created_at: 2026-05-30
updated_at: 2026-05-30
references:
  - "_docs/intent/Workflow/intentional-omission-risk/decision.md"
related_issues: []
related_prs: []
---

# QA Test Plan: `Intentional omission risk`

## Source of Intent

- TODO: `Workflow-Doc-5`
- Plan: None
- Intent: `_docs/intent/Workflow/intentional-omission-risk/decision.md`

## Quality Goal

Small changes should stay lightweight while agents get a clear trigger for recording intentional omissions that future maintainers could mistake for missing work.

## Acceptance Criteria

- AC-001: Fast Track / 小規模変更の説明が、将来の作業者が未実装と誤認しそうな非対応・制限・省略を軽量記録の対象としている。
- AC-002: Agent skills が intentional omission risk を設計判断として扱い、必要に応じて TODO Description / Plan Non-Goals / Intent Alternatives に理由を残すよう案内している。
- AC-003: 必須フィールドや validator 強制を追加せず、既存の docs validation が通る。

## Intent-derived Invariants

- INV-001: Fast Track guidance must not require a dedicated `Why not` field or validator-enforced why-not content for every small task.
- INV-002: Fast Track guidance must tell agents to record rationale when an intentional omission could be mistaken for missing work later.
- INV-003: Docs-prep guidance must allow small tasks to escalate to design-decision documentation when intentional omission risk affects future work.
- INV-004: Agent workflow / skill guidance must keep the lightweight record locations explicit: TODO Description, Plan Non-Goals, or Intent Alternatives / Rationale.

## Risk Assessment

- Risk level: Medium
- Risk rationale: Documentation workflow and agent skill guidance changes can alter future agent behavior.
- Regression risk: Agents could over-escalate small changes or revive heavy why-not recording.
- Data safety risk: None.
- Security / privacy risk: None.
- UX risk: Low; this affects contributor workflow rather than app UI.
- Agent misbehavior risk: Agents may either ignore intentional omissions or require excessive documentation for every small task.

## Test Strategy

- Unit: None; this is a documentation workflow change.
- Integration: Run repository docs validators.
- E2E: None.
- Manual QA: Diff review against Intent and TODO AC.
- Validator / static check: `./scripts/check-docs.sh`.
- Diff review: Confirm no TODO schema field or validator requirement was added.

## Test Matrix

| ID | Source | Requirement / Invariant | Test Type | Command / File | Expected Evidence | Status |
| --- | --- | --- | --- | --- | --- | --- |
| AC-001 | TODO | Fast Track docs mention intentional omissions likely to be mistaken as missing work. | diff review | `_docs/standards/*`, `_docs/documentation_guide.md` | Small-change guidance includes the new trigger without mandatory fields. | planned |
| AC-002 | TODO | Agent skills guide rationale placement for intentional omission risk. | diff review | `.agents/skills/*`, `.claude/skills/*` | Skills mention TODO Description, Plan Non-Goals, or Intent Alternatives / Rationale. | planned |
| AC-003 | TODO | Existing validators still pass and no validator field requirement is added. | validator | `./scripts/check-docs.sh` | Command exits 0. | planned |
| INV-001 | intent | No dedicated `Why not` field or validator-enforced content is required for every small task. | diff review | `TODO.md`, `scripts/*.mjs` | TODO schema and validators are unchanged except task bookkeeping. | planned |
| INV-002 | intent | Fast Track guidance records risky intentional omissions. | diff review | `TODO.md`, `_docs/standards/documentation_operations.md`, `.agents/skills/implementation-prep/SKILL.md` | Fast Track wording includes intentional omission risk. | planned |
| INV-003 | intent | Small tasks can escalate to design-decision documentation when omission risk affects future work. | diff review | `.agents/skills/docs-prep/SKILL.md`, `_docs/standards/documentation_guidelines.md` | Docs-prep / guidelines include the escalation trigger. | planned |
| INV-004 | intent | Lightweight record locations are explicit. | diff review | `_docs/standards/*`, `.agents/skills/*` | TODO Description, Plan Non-Goals, or Intent Alternatives / Rationale are named. | planned |

## Manual QA Checklist

- [ ] Confirm new guidance is a decision axis and not a required field.
- [ ] Confirm wording does not imply every Fast Track task needs an intent document.
- [ ] Confirm `.agents` and `.claude` skill copies remain synchronized.

## Regression Checklist

- [ ] `TODO.md` schema still allows `Plan`, `Intent`, `QA`, and `Verification` to be `None` for Size XS/S and Risk Low.
- [ ] `scripts/validate-todo.mjs` does not gain a why-not field requirement.
- [ ] `scripts/validate-qa.mjs` does not gain semantic why-not enforcement.

## Out of Scope

- Adding a dedicated `Why not` field.
- Adding semantic validator enforcement for why-not quality.
- Creating a plan document for this Size S change.

## Open Questions

- None.
