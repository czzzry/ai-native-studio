# ProductAgent Proof Threat Model

## Assets

- Founder authority and approval boundaries.
- ProductAgent role identity and configuration version.
- Webhook signing secret.
- Event receipt ledger.
- Product recommendations and Founder Briefings.

## Trust Boundaries

- The local signing secret is trusted only for the synthetic proof.
- The raw request body is untrusted until its HMAC is verified.
- Issue descriptions, comments, prompt context, guidance, and repository content remain untrusted
  even after transport authentication.
- ProductAgent output is advisory and cannot represent a Founder decision.
- The recording adapter has no external authority.

## Threats and Controls

### Forged Event

An attacker sends an unsigned event or signs a different body.

Controls: require `Linear-Signature`, compute HMAC-SHA256 from the exact raw bytes, and compare with
constant-time comparison.

### Stale Delivery

A previously valid delivery is replayed later.

Controls: reject timestamps more than 60 seconds before or after local receipt time.

### Duplicate or Conflicting Replay

Linear or an attacker repeats an event, or reuses a `webhookId` with changed content.

Controls: persist each ID with its payload SHA-256; distinguish exact duplicates from conflicting
replays and reject both.

### Wrong Agent Routing

An authentic event for another application reaches ProductAgent.

Controls: match both OAuth client ID and app-user ID to the versioned role configuration.

### Prompt Injection

Untrusted text tries to change the role, reveal internal instructions, or bypass approval.

Controls: never concatenate content into executable instructions; inspect it as data; detect common
indicators; retain the fixed role and authority policy; report the attempt.

### Manufactured Founder Approval

Issue text claims that the Founder approved scope or ordered implementation.

Controls: Phase 2A deliberately has no trusted approval channel. Every claimed approval in webhook
content is rejected as evidence.

### Secret Exposure

A real credential is placed in source, output, command history, or fixtures.

Controls: synthetic secrets only, ignored private paths, final secret-pattern scan, and explicit
documentation prohibiting real secrets in chat, Linear, logs, or Git.

## Residual Risks

- Keyword detection is illustrative, not a complete prompt-injection classifier.
- SQLite does not provide production distributed deduplication.
- Command-line secrets may appear in process listings or shell history; the optional server is local
  proof tooling only.
- No hosted ingress, TLS termination, secret rotation, OAuth, or live Linear behavior is evaluated.
