# Local ProductAgent Proof

## Plain-English Summary

Phase 2A is a working local demonstration of the future `@ProductAgent` boundary. It accepts
synthetic Linear-shaped webhook events, checks that they were signed with the expected local
secret, rejects stale or repeated deliveries, loads a versioned ProductAgent contract, and produces
product questions, recommendations, refusals, safety notes, and the eight-part Founder Briefing.

The proof never calls Linear, GitHub, Gmail, an LLM provider, or any other external service.

## Setup

Create and install the project-local development environment:

```bash
python3 -m venv .venv
.venv/bin/python -m pip install -e '.[dev]'
```

No package is installed globally. The `.venv/` directory is ignored by Git.

## Run the Demonstration

```bash
.venv/bin/product-agent-demo
```

The command runs six synthetic cases:

1. Valid ProductAgent request: accepted and answered.
2. Exact duplicate: rejected.
3. Invalid signature: rejected.
4. Stale signed delivery: rejected.
5. Prompt injection: accepted as product content, but its instructions are ignored.
6. Attempt to commission BuilderAgent: accepted as a request, but the action is refused.

The output explains each decision in plain English and prints the complete Founder Briefing for
accepted events.

## Optional Local HTTP Endpoint

The same service can listen locally at `POST /webhooks/linear`:

```bash
.venv/bin/product-agent-server \
  --secret synthetic-local-only-secret \
  --host 127.0.0.1 \
  --port 8080
```

This command is only for synthetic local experiments. Never pass a real Linear signing secret on
the command line, in chat, in Linear, or in Git.

## What This Phase Proves

- A Linear-shaped event can enter through a small, typed service boundary.
- The raw request body is protected by HMAC-SHA256 verification.
- Events outside a 60-second freshness window are rejected.
- SQLite receipt storage rejects exact duplicates and conflicting `webhookId` replays.
- Events route only to the configured ProductAgent app identity.
- The ProductAgent role contract is versioned and schema-validated.
- Untrusted text cannot grant Founder approval or commission implementation.
- ProductAgent returns structured output and all eight Founder Briefing sections.
- A mock adapter records responses without network access.

## What This Phase Does Not Prove

- Live Linear OAuth installation, webhook delivery, or Agent Session activity creation.
- Secret-manager integration, refresh-token handling, hosting, queues, or production monitoring.
- A trusted mechanism for recording Founder approvals.
- Model-generated product analysis or model safety.
- BuilderAgent, VerifierAgent, GitHub, Gmail, or private-data access.
- Multi-process SQLite behavior, production concurrency, or long-term audit retention.

## Before Live Linear

1. Founder approves Phase 2B and chooses a safe test team or project.
2. Founder manually creates one private Linear OAuth application named `ProductAgent`.
3. A public HTTPS endpoint and managed secret store are selected and approved.
4. The service gains production-grade secret loading, durable storage, structured logging, and
   operational alerts.
5. OAuth callback, installation-token storage, webhook signing-secret rotation, and Agent Activity
   publishing are implemented and tested.
6. The Founder installs the app with only approved teams and least-privilege scopes.
7. A synthetic test issue is used before any real product or private content.

Client secrets, signing secrets, access tokens, and refresh tokens must never be pasted into chat,
Linear issues or comments, source files, logs, or Git history.
