# Product Decision Compiler Implementation Plan

Status: DRAFT — Founder-approved implementation through the read-only adapter slice

## Phase 0: Approve the Slice

Deliverables:

- Founder approval of `product_brief.md` and `acceptance_criteria.yaml`.
- Approval recorded against the immutable commit or artifact version.
- Any material change requires renewed approval.

Exit condition: BuilderAgent has an approved specification and VerifierAgent has the evaluation plan.

## Phase 1: Define the Decision Contract

Deliverables:

- Decision Package, WorkItemEvidence, ConformanceFinding, and DeliveryReport schemas.
- Exact version and content-hash behavior.
- Compatibility mapping from existing Product Brief records.
- Unit tests for valid, incomplete, superseded, and conflicting versions.

Exit condition: schemas reject malformed authority, missing scope, and unknown versions without model
involvement.

## Phase 2: Build the Synthetic Event Path

Deliverables:

- Synthetic Linear-shaped project, issue, and sub-issue fixtures.
- Intake, freshness, deduplication, and provenance handling.
- Linkage from each work item to a Decision Package version.
- No-network adapter and replayable demo command.

Exit condition: one command runs the complete fixture set offline.

## Phase 3: Implement Conformance Evaluation

Deliverables:

- Stable finding classifications and severity rules.
- Aligned, clarification, scope expansion, contradiction, risk, missing-evidence, and stale-version
  cases.
- Strict output validation for any model-assisted comparison path.
- Regression fixtures for prompt injection and forged approval text.

Exit condition: every required classification has a deterministic test and evidence excerpt.

## Phase 4: Implement the PO Digest

Deliverables:

- Quiet-by-default digest formatter.
- Grouping by decision and severity.
- Summary of aligned work without listing every event.
- Explicit next actions: accept, amend, investigate.

Exit condition: the demo produces a concise digest with the deliberate scope violation and no noisy
activity replay.

## Phase 5: Delivery Evidence and Independent Verification

Deliverables:

- Delivery Report validation and comparison.
- Full acceptance and threat-model test run.
- VerifierAgent PASS or FAIL report with evidence, residual risks, and release recommendation.

Exit condition: no unresolved required acceptance criterion and no unauthorised release behavior.

## Phase 6: Public Packaging

Deliverables after verification:

- Public README centered on the Alignment Proof.
- Safe synthetic fixtures and reproducible demo instructions.
- Architecture, threat model, evaluation results, and limitations.
- LICENSE, CONTRIBUTING, SECURITY, and CI setup.
- History and repository metadata review for personal information.
- Read-only Linear and GitHub adapter code with synthetic provider responses.

Exit condition: Founder approves publication of the verified public slice.

## Phase 7: Read-only Provider Adapters

Deliverables:

- Explicit decision markers for conservative matching of provider records.
- Linear reads for issues and sub-issues.
- GitHub reads for issues, pull requests, commits, changed files, and check runs.
- Normalisation into the existing WorkItemEvidence and DeliveryReport contracts.
- Tests proving no provider write method is used and stale decision markers remain visible.

Exit condition: a no-network integration demo exercises both adapters and the same conformance
engine used by the offline proof.

## Explicitly Not in This Plan

- Live Linear OAuth, webhooks, and incremental synchronisation.
- Automatic issue creation in a personal or private workspace.
- Automatic agent dispatch.
- Automatic release or merge.
- Public exposure of private history, tokens, real issue content, or personal identifiers.
