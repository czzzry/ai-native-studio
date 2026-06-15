# ProductAgent Proof Evaluation Plan

## Evaluation Objective

Show reproducibly that the local proof enforces webhook authenticity, event freshness, deduplication,
role routing, ProductAgent authority, untrusted-input treatment, and reporting structure.

## Synthetic Test Groups

- Valid signed request.
- Invalid signature.
- Missing signature.
- Timestamp outside the 60-second tolerance.
- Exact duplicate `webhookId` and payload.
- Conflicting replay using the same `webhookId` with a changed payload.
- Correct ProductAgent role and version routing.
- Prompt injection in issue and comment text.
- Attempt to override Founder authority.
- Attempt to commission BuilderAgent without Founder approval.
- Founder Briefing with all eight required fields.

## Acceptance Criteria

- All automated tests pass.
- Ruff reports no lint findings.
- Python imports and byte compilation succeed.
- The demonstration runs all six cases without external access.
- Authentic valid requests produce questions, recommendations, non-decisions, and a Founder Briefing.
- Forged, stale, duplicate, and replay-conflict events are rejected with clear reasons.
- Injection and implementation requests do not change role authority or create approvals.
- No secret-like values or private-data files are committed.

## Evidence Commands

```bash
.venv/bin/python -m pytest
.venv/bin/python -m ruff check .
.venv/bin/python -m compileall -q src tests
.venv/bin/product-agent-demo
git diff --check
```

## Limitations

This evaluation tests deterministic local code and synthetic events. It does not measure live Linear
delivery, model quality, product recommendation quality, hosted reliability, or production security.
