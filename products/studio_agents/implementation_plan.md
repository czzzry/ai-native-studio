# Studio Agents Implementation Plan

## Phase 2A: Runnable Local ProductAgent Proof

Status: implemented in this phase.

Deliverables:

- Strict synthetic Linear event models.
- HMAC and timestamp verification.
- SQLite duplicate and replay ledger.
- Versioned ProductAgent role configuration.
- Deterministic Founder-authority policy.
- Mockable Linear adapter.
- Local HTTP endpoint and complete demonstration command.
- Automated security, routing, authority, and Founder Briefing tests.

Exit criteria:

- Required tests, linting, imports, demonstration, diff checks, and secret checks pass.
- No external system is contacted or changed.
- Founder receives the commit and evidence for review.

Rollback:

- Revert the Phase 2A commit. No external state or credentials require cleanup.

## Phase 2B: One Live Test ProductAgent

Objective: connect one private Linear `ProductAgent` application to a safe hosted test endpoint.

Dependencies:

- Explicit Founder approval.
- Manually created private Linear OAuth application.
- Approved hosting and managed secret storage.
- Public HTTPS callback and webhook URLs.
- OAuth installation flow, encrypted token storage, Agent Activity publishing, and operational logs.
- Synthetic Linear test project or issue with no private product data.

Security boundary:

- ProductAgent only; no BuilderAgent, VerifierAgent, GitHub write, Gmail, or private email access.
- Least-privilege Linear scopes and test-team-only access.
- Secrets never enter chat, Linear content, source files, application logs, or Git history.

Rollback:

- Suspend or uninstall the test app, revoke its OAuth grant, delete hosted secrets and test storage,
  and disable the endpoint.
