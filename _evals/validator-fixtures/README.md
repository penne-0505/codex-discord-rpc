# Validator fixtures

These fixtures exercise the repository validators themselves.

They are not active project tasks or QA records. `scripts/test-validators.ts`
runs the validators against these files and expects:

- files under `valid/` to pass;
- files under `invalid/` to fail.

The intent, QA, and frontmatter fixtures run through their validators with
`--fixture` and use `fixture_path` front matter so the validators can apply the
normal canonical-path rules while the fixture files remain under `_evals/`.

The project-retained `known/` and `unknown/` frontmatter marker fixtures remain
active alongside upstream `valid/` and `invalid/` cases. They verify that
`intent_schema` and `qa_schema` are accepted only on their canonical document
kinds, while an unrelated future marker is rejected as an unknown field.

Frontmatter fixtures also cover duplicate fields, wrong types, and cross-kind
schema marker placement.

The QA invalid fixture without `qa_schema` also verifies legacy compatibility:
legacy plans still require an `INV-*`, while schema v2 accepts `None`.
