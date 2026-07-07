---
title: "QA Verification: Intentional omission risk"
status: active
draft_status: n/a
qa_status: verified
risk: Medium
created_at: 2026-05-30
updated_at: 2026-05-30
references:
  - "_docs/intent/Workflow/intentional-omission-risk/decision.md"
  - "_docs/qa/Workflow/intentional-omission-risk/test-plan.md"
related_issues: []
related_prs: []
---

# QA Verification: `Intentional omission risk`

## Summary

Fast Track の軽量性を保ったまま、将来の作業者が未実装と誤認しそうな intentional omission を軽量記録または Intent へ昇格する判定軸を standards / guide / skills / evals に追加した。

## Verification Verdict

Verdict: PASS

## Commands Run

```bash
./scripts/check-docs.sh
git diff --check
diff -qr .agents/skills .claude/skills
git diff -- scripts/*.mjs
```

Result:

```text
./scripts/check-docs.sh: exit 0; validator self-tests passed for TODO and QA fixtures.
git diff --check: exit 0; no whitespace errors.
diff -qr .agents/skills .claude/skills: exit 0; no differences reported.
git diff -- scripts/*.mjs: exit 0; no script diff, so no validator enforcement was added.
```

## Automated Test Results

| Command / Test | Result | Notes |
| --- | --- | --- |
| `./scripts/check-docs.sh` | PASS | Docs validators and fixture self-tests passed. |
| `git diff --check` | PASS | No whitespace errors. |
| `diff -qr .agents/skills .claude/skills` | PASS | Skill trees remain synchronized. |
| `git diff -- scripts/*.mjs` | PASS | No validator or script changes were introduced. |

## Manual QA Results

| Checklist Item | Result | Notes |
| --- | --- | --- |
| Confirm new guidance is a decision axis and not a required field. | PASS | TODO schema fields are unchanged; wording points to existing Description / PR / commit / Plan / Intent locations. |
| Confirm wording does not imply every Fast Track task needs an intent document. | PASS | Fast Track still allows Plan / Intent / QA to be `None`; only future-misread omissions trigger rationale. |
| Confirm `.agents` and `.claude` skill copies remain synchronized. | PASS | `diff -qr` produced no differences. |

## Acceptance Criteria Coverage

| ID | Result | Evidence |
| --- | --- | --- |
| AC-001 | PASS | `TODO.md`, `_docs/standards/documentation_operations.md`, `_docs/standards/documentation_guidelines.md`, `_docs/standards/quality_assurance.md`, and `_docs/documentation_guide.md` now mention intentional omission risk in small-change / Fast Track guidance. |
| AC-002 | PASS | `implementation-prep`, `docs-prep`, `qa-prep`, and `qa-review` skills now route intentional omissions through lightweight notes or design-decision docs. |
| AC-003 | PASS | No `scripts/*.mjs` diff; `./scripts/check-docs.sh` passed. |

## Invariant Coverage

| ID | Result | Evidence |
| --- | --- | --- |
| INV-001 | PASS | No dedicated why-not field or validator requirement was added. |
| INV-002 | PASS | Fast Track guidance now tells agents to record rationale when deliberate omissions could be mistaken for missing work. |
| INV-003 | PASS | `docs-prep` allows small tasks to escalate when intentional omission risk affects future work. |
| INV-004 | PASS | Lightweight record locations are named: TODO Description, PR / commit notes, Plan Non-Goals, and Intent Alternatives / Rationale. |

## Deferred / Not Covered

| ID | Reason | Follow-up |
| --- | --- | --- |
| None | None | None |

## Residual Risks

None

## Follow-up TODOs

None
