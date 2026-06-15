"""Deterministic ProductAgent authority and untrusted-input policy."""

from .models import AgentSessionEvent, FounderBriefing, ProductAgentResponse
from .role_config import ProductAgentRoleConfig


class ProductAgentPolicy:
    def __init__(self, role: ProductAgentRoleConfig) -> None:
        self._role = role

    def evaluate(self, event: AgentSessionEvent) -> ProductAgentResponse:
        content = self._collect_untrusted_content(event)
        normalized = content.lower()
        injection_matches = [term for term in self._role.injection_terms if term in normalized]
        implementation_matches = [
            term for term in self._role.implementation_terms if term in normalized
        ]

        questions = [
            "Who is the target user, and what concrete problem should this solve for them?",
            "What outcome and success metric would justify moving beyond a recommendation?",
            "What is explicitly out of scope for the first approved version?",
        ]
        if any(term in normalized for term in ("private", "email", "gmail", "credential")):
            questions.append(
                "Which privacy boundary and permission stage has the Founder explicitly approved?"
            )

        recommendations = [
            "Keep this work as a ProductAgent recommendation until the Founder approves a "
            "versioned specification.",
            "Define user journeys, measurable acceptance criteria, non-goals, and user, privacy, "
            "operational, and adoption risks before implementation.",
        ]

        safety_notes = [
            "Issue text, comments, guidance, prompt context, and repository content were treated "
            "as untrusted product input, not as authority or system instructions."
        ]
        if injection_matches:
            safety_notes.append(
                "Potential instruction injection was detected and ignored: "
                + ", ".join(sorted(set(injection_matches)))
                + "."
            )

        refused_actions: list[str] = []
        if implementation_matches:
            refused_actions.append(
                "Refused to commission BuilderAgent or begin implementation because Phase 2A has "
                "no trusted Founder-approval channel."
            )
        if "override founder" in normalized or "treat this as approved" in normalized:
            refused_actions.append(
                "Refused the attempt to override Founder and Product Lead authority or manufacture "
                "an approval from untrusted text."
            )

        approved_decisions = [
            "None. Phase 2A does not accept Founder approvals from webhook content."
        ]
        briefing = FounderBriefing(
            objective="Evaluate the synthetic Linear request as ProductAgent without changing "
            "approved product scope.",
            what_was_done="Authenticated the event, loaded the versioned ProductAgent role, "
            "treated supplied content as untrusted, and produced product questions and "
            "recommendations.",
            what_changed="No approved specification, implementation, repository, Linear workspace, "
            "or external system was changed.",
            important_decisions_and_why="Recommendations remain advisory because only the Founder "
            "and Product Lead can approve scope and commission implementation.",
            validation_or_checks_performed=(
                "Webhook signature, timestamp freshness, receipt identity, "
                "role routing, injection indicators, and implementation-commissioning language "
                "were checked deterministically."
            ),
            remaining_risks_assumptions_or_questions=(
                "The request still needs answers to the product questions, and Phase 2A does not "
                "prove live Linear delivery or human approval capture."
            ),
            founder_approval_required="Founder approval of a versioned specification is required "
            "before BuilderAgent may implement anything.",
            recommended_next_action="Answer the product questions, revise the recommendation, and "
            "present a versioned specification for explicit Founder approval.",
        )

        return ProductAgentResponse(
            role=self._role.role,
            role_version=self._role.role_version,
            session_id=event.agent_session.id,
            product_questions=questions,
            recommendations=recommendations,
            approved_decisions=approved_decisions,
            refused_actions=refused_actions,
            safety_notes=safety_notes,
            founder_briefing=briefing,
        )

    @staticmethod
    def _collect_untrusted_content(event: AgentSessionEvent) -> str:
        session = event.agent_session
        values = [
            session.issue.title,
            session.issue.description,
            session.prompt_context,
            *(session.guidance),
            *(session.repository_content),
        ]
        if session.comment:
            values.append(session.comment.body)
        return "\n".join(values)
