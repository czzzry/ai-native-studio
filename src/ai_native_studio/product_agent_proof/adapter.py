"""Mockable boundary for future Linear response publication."""

from dataclasses import dataclass, field
from typing import Protocol

from .models import ProductAgentResponse


class LinearAdapter(Protocol):
    def publish_response(self, session_id: str, response: ProductAgentResponse) -> None:
        """Publish a response for an agent session."""


@dataclass
class RecordingLinearAdapter:
    """Local adapter that records output without making network calls."""

    published: list[tuple[str, ProductAgentResponse]] = field(default_factory=list)

    def publish_response(self, session_id: str, response: ProductAgentResponse) -> None:
        self.published.append((session_id, response))
