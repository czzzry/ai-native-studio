"""Conversation-state extraction helpers for ProductAgent."""

from __future__ import annotations

import re
from collections.abc import Sequence

from pydantic import Field

from .models import StrictModel


class ConversationDecisionLedger(StrictModel):
    target_user: str | None = None
    initial_provider: str | None = None
    future_provider: str | None = None
    primary_job: str | None = None
    in_scope_actions: list[str] = Field(default_factory=list)
    out_of_scope_actions: list[str] = Field(default_factory=list)
    allowed_initial_permissions: list[str] = Field(default_factory=list)
    prohibited_initial_permissions: list[str] = Field(default_factory=list)
    review_model: str | None = None
    delete_gate: str | None = None
    approval_model: str | None = None
    failure_modes: list[str] = Field(default_factory=list)
    unresolved_questions: list[str] = Field(default_factory=list)
    founder_confirmed_decisions: list[str] = Field(default_factory=list)


_NORMALIZE_SPACE = re.compile(r"\s+")


def _normalize(text: str) -> str:
    return _NORMALIZE_SPACE.sub(" ", text).strip().lower()


def build_conversation_decision_ledger(texts: Sequence[str]) -> ConversationDecisionLedger:
    combined = "\n".join(text for text in texts if text).strip()
    normalized = _normalize(combined)
    ledger = ConversationDecisionLedger()

    if not combined:
        return ledger

    if any(marker in normalized for marker in ("just me", "only me", "founder only")):
        ledger.target_user = "Founder only"
        ledger.founder_confirmed_decisions.append("The first user is the Founder only.")

    if "gmail" in normalized:
        ledger.initial_provider = "Gmail"
        ledger.founder_confirmed_decisions.append("The initial provider is Gmail.")
    if "protonmail" in normalized:
        ledger.future_provider = "ProtonMail"
        ledger.founder_confirmed_decisions.append("The later provider is ProtonMail.")
    if ledger.initial_provider and ledger.future_provider:
        ledger.founder_confirmed_decisions.append(
            "Gmail comes first and ProtonMail comes later."
        )

    if any(
        marker in normalized
        for marker in ("triage", "label", "categorize", "categorize", "spam", "unsubscribe")
    ):
        ledger.primary_job = "triage, label, categorize, and handle spam/unsubscribe"
        ledger.in_scope_actions.extend(
            action
            for action, marker in (
                ("triage", "triage"),
                ("label", "label"),
                ("categorize", "categorize"),
                ("spam handling", "spam"),
                ("unsubscribe handling", "unsubscribe"),
            )
            if marker in normalized
        )
        ledger.founder_confirmed_decisions.append(
            "The primary job is inbox triage, labeling, categorization, "
            "and spam/unsubscribe handling."
        )

    if any(
        marker in normalized
        for marker in ("read-only", "move messages into folders", "move into folders")
    ):
        ledger.allowed_initial_permissions.extend(
            [
                "read-only access",
                "move messages into folders or labels",
            ]
        )
        ledger.founder_confirmed_decisions.append(
            "The initial authority is read-only plus folder or label movement."
        )

    if "folder creation" in normalized or "folder creation and movement" in normalized:
        ledger.allowed_initial_permissions.append("create folders for review and routing")
        ledger.founder_confirmed_decisions.append(
            "Folder creation and movement do not require separate approval."
        )

    if "delete" in normalized:
        ledger.prohibited_initial_permissions.append("delete messages")
        if "probably delete" in normalized:
            ledger.in_scope_actions.append("review-only probably-delete folder")
    if (
        "delete authority" in normalized
        or "two weeks" in normalized
        or "100% accuracy" in normalized
    ):
        ledger.delete_gate = "Only after roughly 100% accuracy for about two weeks."
        ledger.founder_confirmed_decisions.append(
            "Delete authority is gated behind roughly 100% accuracy for about two weeks."
        )

    if (
        "user checks folders before granting real responsibility" in normalized
        or "review model" in normalized
    ):
        ledger.review_model = "Founder reviews folders before granting real responsibility."
        ledger.founder_confirmed_decisions.append(
            "The review model is user folder review before broader responsibility."
        )

    if "bulk approval" in normalized or "not per-email" in normalized:
        ledger.approval_model = "Bulk approval, not per-email."
        ledger.founder_confirmed_decisions.append("Approval is bulk, not per-email.")

    if "miscategorization" in normalized:
        ledger.failure_modes.append("miscategorization")
    if "deleting email that should not be deleted" in normalized or "delete email" in normalized:
        ledger.failure_modes.append("deleting email that should not be deleted")
    if ledger.failure_modes:
        ledger.founder_confirmed_decisions.append(
            "The main failure mode is miscategorization and accidental deletion."
        )

    if "no approval required for folder creation and movement" in normalized:
        ledger.allowed_initial_permissions.append(
            "folder creation and movement without additional approval"
        )
    if "spam/unsubscribe explicitly confirmed as in scope" in normalized:
        ledger.in_scope_actions.extend(["spam handling", "unsubscribe handling"])

    ledger.in_scope_actions = list(dict.fromkeys(ledger.in_scope_actions))
    ledger.out_of_scope_actions = list(dict.fromkeys(ledger.out_of_scope_actions))
    ledger.allowed_initial_permissions = list(
        dict.fromkeys(ledger.allowed_initial_permissions)
    )
    ledger.prohibited_initial_permissions = list(
        dict.fromkeys(ledger.prohibited_initial_permissions)
    )
    ledger.failure_modes = list(dict.fromkeys(ledger.failure_modes))
    ledger.founder_confirmed_decisions = list(
        dict.fromkeys(ledger.founder_confirmed_decisions)
    )

    if not ledger.unresolved_questions:
        if ledger.initial_provider and ledger.target_user and ledger.primary_job:
            ledger.unresolved_questions.extend(
                [
                    "Exact folder taxonomy and review bucket naming.",
                    "Exact accuracy metric for graduation to delete authority.",
                ]
            )
        else:
            ledger.unresolved_questions.extend(
                [
                    "Exact folder taxonomy and review bucket naming.",
                    "Exact measurement for the permissions review gate.",
                ]
            )

    return ledger


def render_decision_ledger(ledger: ConversationDecisionLedger) -> str:
    lines = [
        "Decision ledger:",
        f"- target_user: {ledger.target_user or 'unresolved'}",
        f"- initial_provider: {ledger.initial_provider or 'unresolved'}",
        f"- future_provider: {ledger.future_provider or 'unresolved'}",
        f"- primary_job: {ledger.primary_job or 'unresolved'}",
        f"- in_scope_actions: {', '.join(ledger.in_scope_actions) or 'unresolved'}",
        f"- out_of_scope_actions: {', '.join(ledger.out_of_scope_actions) or 'unresolved'}",
        (
            "- allowed_initial_permissions: "
            + (", ".join(ledger.allowed_initial_permissions) or "unresolved")
        ),
        (
            "- prohibited_initial_permissions: "
            + (", ".join(ledger.prohibited_initial_permissions) or "unresolved")
        ),
        f"- review_model: {ledger.review_model or 'unresolved'}",
        f"- delete_gate: {ledger.delete_gate or 'unresolved'}",
        f"- approval_model: {ledger.approval_model or 'unresolved'}",
        f"- failure_modes: {', '.join(ledger.failure_modes) or 'unresolved'}",
    ]
    if ledger.founder_confirmed_decisions:
        lines.extend(["- founder_confirmed_decisions:"])
        lines.extend(f"  - {item}" for item in ledger.founder_confirmed_decisions)
    if ledger.unresolved_questions:
        lines.extend(["- unresolved_questions:"])
        lines.extend(f"  - {item}" for item in ledger.unresolved_questions)
    return "\n".join(lines)


def summarize_decision_ledger(ledger: ConversationDecisionLedger) -> str:
    parts: list[str] = []
    if ledger.target_user:
        parts.append(f"Target user: {ledger.target_user}.")
    if ledger.initial_provider:
        parts.append(f"Initial provider: {ledger.initial_provider}.")
    if ledger.future_provider:
        parts.append(f"Future provider: {ledger.future_provider}.")
    if ledger.primary_job:
        parts.append(f"Primary job: {ledger.primary_job}.")
    if ledger.allowed_initial_permissions:
        parts.append(
            "Allowed initial permissions: "
            + ", ".join(ledger.allowed_initial_permissions)
            + "."
        )
    if ledger.prohibited_initial_permissions:
        parts.append(
            "Prohibited initial permissions: "
            + ", ".join(ledger.prohibited_initial_permissions)
            + "."
        )
    if ledger.review_model:
        parts.append(f"Review model: {ledger.review_model}.")
    if ledger.delete_gate:
        parts.append(f"Delete gate: {ledger.delete_gate}.")
    if ledger.approval_model:
        parts.append(f"Approval model: {ledger.approval_model}.")
    if ledger.failure_modes:
        parts.append("Failure modes: " + ", ".join(ledger.failure_modes) + ".")
    if ledger.unresolved_questions:
        parts.append("Unresolved questions: " + ", ".join(ledger.unresolved_questions) + ".")
    return " ".join(parts)
