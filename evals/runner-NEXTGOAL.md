# NEXTGOAL: Clamp discounts

## Goal

Discounts above 100% or below 0% never produce a negative or inflated order total.

## Context

- Repo state: tinyshop, branch main
- Relevant files: src/tinyshop/pricing.py, tests/test_pricing.py
- Decisions to respect: docs/adr/0001-money-in-cents.md (int cents only)

## Acceptance checklist

- [ ] apply_discount(1000, 150) returns 0 — proven by `uv run pytest tests/test_pricing.py` exits 0
- [ ] apply_discount(1000, -10) returns 1000 — proven by `uv run pytest tests/test_pricing.py` exits 0

## Verification

`uv run pytest` exits 0; show the output in the transcript.

## Guardrails

- No test is deleted, skipped, or weakened to make a check pass.
- No edits outside src/tinyshop/pricing.py and tests/.
- Amounts stay int cents.

## Out of scope

- Changing the Order dataclass

## Open questions

None

## Condition

```text
New tests in tests/test_pricing.py prove apply_discount clamps percent to 0..100 (150% gives 0, -10% gives the full total), and `uv run pytest` exits 0 with its output shown in the transcript; guardrails: no test deleted, skipped or weakened, edits only in src/tinyshop/pricing.py and tests/, amounts stay int cents; out of scope: Order dataclass. Or stop after 15 turns and report what remains.
```
