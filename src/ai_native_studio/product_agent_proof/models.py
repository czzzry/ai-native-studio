"""Structured inputs and outputs for the ProductAgent proof."""

from typing import Literal

from pydantic import BaseModel, ConfigDict, Field


class StrictModel(BaseModel):
    """Reject unexpected fields so synthetic fixtures stay explicit."""

    model_config = ConfigDict(extra="forbid", populate_by_name=True)


class LinearIssue(StrictModel):
    id: str
    identifier: str
    title: str
    description: str = ""


class LinearComment(StrictModel):
    id: str
    body: str


class AgentSession(StrictModel):
    id: str
    issue: LinearIssue
    comment: LinearComment | None = None
    prompt_context: str = Field(default="", alias="promptContext")
    guidance: list[str] = Field(default_factory=list)
    repository_content: list[str] = Field(default_factory=list, alias="repositoryContent")


class AgentSessionEvent(StrictModel):
    type: Literal["AgentSessionEvent"]
    action: Literal["created", "prompted"]
    webhook_id: str = Field(alias="webhookId")
    webhook_timestamp: int = Field(alias="webhookTimestamp")
    oauth_client_id: str = Field(alias="oauthClientId")
    app_user_id: str = Field(alias="appUserId")
    agent_session: AgentSession = Field(alias="agentSession")


class FounderBriefing(StrictModel):
    objective: str
    what_was_done: str
    what_changed: str
    important_decisions_and_why: str
    validation_or_checks_performed: str
    remaining_risks_assumptions_or_questions: str
    founder_approval_required: str
    recommended_next_action: str


class ProductAgentResponse(StrictModel):
    role: Literal["ProductAgent"]
    role_version: str
    session_id: str
    product_questions: list[str]
    recommendations: list[str]
    approved_decisions: list[str]
    refused_actions: list[str]
    safety_notes: list[str]
    founder_briefing: FounderBriefing


class WebhookResult(StrictModel):
    status: Literal["accepted", "rejected"]
    code: str
    reason: str
    http_status: int
    response: ProductAgentResponse | None = None
