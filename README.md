# Product Decision Compiler

> AI can make software cheap to produce. This keeps product decisions expensive to ignore.

Product Decision Compiler is a small, runnable proof for product owners and PMs working with
AI-first engineering teams.

It answers one practical question:

**Is the work still the thing we agreed to build?**

## Why this exists

When agents can create issues, pull requests, and commits all day, activity grows faster than
attention. A PO should not have to read every update or trust every polished summary.

This project turns an approved product decision into a durable contract. It then checks agent-shaped
work against that contract and surfaces only what needs human judgment: scope drift, risk, or missing
delivery evidence.

The goal is not more activity. The goal is a quieter, more useful product review.

## The loop

```text
PO intent → Decision Package → Founder approval → AI-built work → PO digest
```

The compiler does not approve its own interpretation, rewrite scope, create tickets, add comments,
or release software. People still decide.

## What works today

The local proof can:

- turn structured product intent into a versioned Decision Package
- record approval for one exact decision version
- identify aligned work, scope expansion, clarification, security risk, and contradictions
- connect delivery evidence to acceptance criteria
- reject duplicate events, replay conflicts, stale versions, and embedded instructions such as
  “approve this”
- suppress routine aligned activity and produce a short PO digest

The real-provider adapters are deliberately read-only:

- Linear: reads linked issues and sub-issues
- GitHub: reads linked issues, pull requests, commits, changed files, and check runs
- Issues and pull requests: require an explicit marker such as `decision:onboarding-improvement-v1`
- GitHub commits: can carry their own marker or inherit the link from a marked pull request
- Neither: creates, updates, comments on, labels, or moves anything

## See it in a minute

```bash
python3 -m venv .venv
.venv/bin/python -m pip install -e '.[dev]'
.venv/bin/product-decision-compiler-demo
.venv/bin/product-decision-compiler-integrations-demo
```

The first command runs the core proof with synthetic Linear-shaped work. The second runs the
read-only Linear and GitHub adapters against synthetic provider responses, so it needs no accounts,
network access, or secrets.

You should see a PO digest rather than an activity feed:

```text
3 finding(s) require PO attention
• risk / high — Work touches a security-sensitive area outside the decision.
```

Run the full test suite with:

```bash
.venv/bin/python -m pytest -p no:cacheprovider tests
```

## Using real read-only data

The adapters are small Python building blocks, not a hosted app. They accept `LINEAR_API_KEY` and
an optional `GITHUB_TOKEN`, fetch up to 100 records per call, and return the same evidence models
used by the offline proof. The Linear adapter takes a Linear team ID.

The intended flow is:

1. Approve a Decision Package.
2. Put its marker in the Linear issue or GitHub issue/PR body.
3. Read the provider records with the adapter.
4. Pass the normalised evidence to `ConformanceEngine`.
5. Give the resulting digest to the PO.

No provider write scope is needed for this stage.

## Design in one sentence

**AI can help frame the decision; deterministic code guards it; a human remains the authority.**

That boundary is the point of the project. The compiler itself does not need a model to prove the
workflow, which keeps the important checks repeatable and inspectable.

## What this is — and is not

This is an open engineering proof of a product-operations idea. It is not a production release gate,
an autonomous PM, a chatbot, or a live hosted Linear/GitHub application. Authentication, scheduling,
pagination beyond the first page, webhook processing, and a durable external store remain follow-on
work.

## Read the evidence

- [Product Decision Compiler brief](products/decision_compiler/product_brief.md)
- [Architecture](products/decision_compiler/architecture.md)
- [Acceptance criteria](products/decision_compiler/acceptance_criteria.yaml)
- [Evaluation plan](products/decision_compiler/eval_plan.md)
- [Public product write-up](docs/public/product-decision-compiler.md)
- [Read-only adapter code](src/ai_native_studio/product_decision_compiler/integrations.py)
- [Tests](tests/product_decision_compiler/)

The repository also contains the earlier ProductAgent foundation. It is useful context, but the
Product Decision Compiler is the public centre of gravity.

## License

MIT. Use it, change it, build on it, or sell it. Keep the copyright and license notice with it.
