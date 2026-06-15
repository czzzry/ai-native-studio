# Studio Agent Proof Architecture

## Goal

Demonstrate the smallest executable boundary for a founder-led ProductAgent without live Linear,
external models, hosting, or private data.

## Runtime Flow

1. A synthetic `AgentSessionEvent` is serialized as a raw JSON request body.
2. `ProductAgentWebhookService` verifies the `Linear-Signature` HMAC before trusting the body.
3. The event is parsed into strict Pydantic models.
4. The timestamp must be within 60 seconds of local receipt time.
5. A SQLite receipt ledger reserves `webhookId` with the payload hash.
6. Exact repeats are rejected as duplicates; changed payloads reusing an ID are rejected as replay
   conflicts.
7. The event's OAuth client and app-user IDs must match the versioned ProductAgent configuration.
8. Deterministic policy treats all issue, comment, guidance, prompt, and repository text as untrusted.
9. ProductAgent produces questions, recommendations, explicit non-decisions, refusals, safety notes,
   and a Founder Briefing.
10. `RecordingLinearAdapter` records the response in memory instead of making a network call.

## Components

- `models.py`: strict request, ProductAgent response, and Founder Briefing schemas.
- `security.py`: HMAC-SHA256 and timestamp validation.
- `dedup.py`: minimal SQLite receipt ledger.
- `role_config.py` and `config/product_agent.v1.json`: versioned role identity and policy terms.
- `policy.py`: deterministic Founder-authority and untrusted-input controls.
- `adapter.py`: protocol plus no-network recording implementation.
- `service.py`: orchestration and clear rejection results.
- `server.py`: optional standard-library local HTTP endpoint.
- `demo.py`: deterministic six-case demonstration.

## Important Design Decisions

- No web framework: the standard library is sufficient for this proof and reduces dependencies.
- No LLM: deterministic behavior makes the authority and security controls directly testable.
- No approval parsing: Phase 2A has no trusted approval channel, so text claiming Founder approval is
  never accepted as evidence.
- Reserve before policy execution: once an authentic fresh event ID is seen, altered retries cannot
  cause a second execution.
- Mock adapter: the service boundary is ready for a future Linear implementation without accidental
  live calls in this phase.

## Local Persistence

The demonstration uses an in-memory SQLite database. The optional server defaults to
`data/private/product_agent_proof.sqlite3`, which is ignored by Git. SQLite is appropriate for a
single local process but is not the recommended production receipt store.
