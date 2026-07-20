from __future__ import annotations

from collections.abc import Mapping
from urllib.parse import urlsplit

from ai_native_studio.product_decision_compiler.contracts import (
    DecisionPackageService,
    InMemoryDecisionPackageStore,
)
from ai_native_studio.product_decision_compiler.fixtures import load_fixture
from ai_native_studio.product_decision_compiler.integrations import (
    DecisionBinding,
    GitHubReadOnlyAdapter,
    LinearReadOnlyAdapter,
    extract_decision_reference,
)


class FakeTransport:
    def __init__(self, responses: Mapping[str, object]) -> None:
        self.responses = responses
        self.requests: list[tuple[str, str, dict[str, str], bytes | None]] = []

    def request(
        self,
        *,
        method: str,
        url: str,
        headers: Mapping[str, str],
        payload: bytes | None = None,
    ) -> object:
        self.requests.append((method, url, dict(headers), payload))
        key = "graphql" if method == "POST" else urlsplit(url).path
        return self.responses[key]


def _package():
    fixture = load_fixture()
    service = DecisionPackageService(InMemoryDecisionPackageStore())
    created = service.create_or_reuse(
        decision_id=fixture.decision_id,
        source_id=fixture.source_id,
        draft=fixture.decision,
        created_at_ms=1_700_000_000_000,
    )
    approval = service.approve(
        founder_id="founder",
        product_agent_id="agent",
        version_id=created.package.version_id,
        source_event_id="approval",
        approved_at_ms=1_700_000_000_001,
    )
    assert approval.package is not None
    return approval.package


def test_decision_markers_are_explicit_and_preserve_stale_versions() -> None:
    assert extract_decision_reference("decision:onboarding-v1") is not None
    assert extract_decision_reference("pdc: onboarding-v2") is not None
    assert extract_decision_reference("onboarding-v1") is None

    binding = DecisionBinding(decision_id="onboarding", decision_version=1)
    current = binding.reference_for("decision:onboarding-v1")
    stale = binding.reference_for("decision:onboarding-v2")
    unrelated = binding.reference_for("decision:billing-v1")

    assert current is not None and current.version_id == "onboarding-v1"
    assert stale is not None and stale.decision_version == 2
    assert unrelated is None


def test_linear_adapter_reads_and_normalises_linked_issues() -> None:
    transport = FakeTransport(
        {
            "graphql": {
                "data": {
                    "team": {
                        "issues": {
                            "nodes": [
                                {
                                    "id": "lin-1",
                                    "identifier": "STU-101",
                                    "title": "Improve mobile onboarding",
                                    "description": (
                                        "decision:onboarding-improvement-v1\nResume behavior"
                                    ),
                                    "url": "https://linear.app/studio/issue/STU-101",
                                    "createdAt": "2026-07-20T09:00:00Z",
                                    "updatedAt": "2026-07-20T10:00:00Z",
                                    "project": {"name": "Onboarding"},
                                    "parent": {"identifier": "STU-100"},
                                    "labels": {"nodes": [{"name": "agentic"}]},
                                },
                                {
                                    "id": "lin-2",
                                    "identifier": "STU-102",
                                    "title": "Unrelated cleanup",
                                    "description": "No decision link.",
                                    "url": "https://linear.app/studio/issue/STU-102",
                                    "createdAt": "2026-07-20T09:00:00Z",
                                    "updatedAt": "2026-07-20T10:00:00Z",
                                    "project": None,
                                    "parent": None,
                                    "labels": {"nodes": []},
                                },
                            ]
                        }
                    }
                }
            }
        }
    )
    batch = LinearReadOnlyAdapter(
        "linear-test-token",
        endpoint="https://linear.test/graphql",
        transport=transport,
    ).collect_for_decision(_package(), team_id="team-studio")

    assert len(batch.work_items) == 1
    assert batch.work_items[0].source_type == "sub_issue"
    assert batch.work_items[0].source_id == "STU-101"
    assert batch.unmatched_records == 1
    assert transport.requests[0][0] == "POST"
    assert transport.requests[0][2]["Authorization"] == "linear-test-token"
    assert "mutation" not in (transport.requests[0][3] or b"").decode().lower()


def test_github_adapter_matches_issue_pr_commit_and_delivery_evidence() -> None:
    commit_sha = "abcdef1234567890"
    responses = {
        "/repos/acme/demo/issues": [
            {
                "number": 12,
                "title": "Onboarding issue",
                "body": "decision:onboarding-improvement-v1\nAcceptance: resume onboarding",
                "html_url": "https://github.com/acme/demo/issues/12",
                "created_at": "2026-07-20T09:00:00Z",
                "updated_at": "2026-07-20T10:00:00Z",
            },
            {
                "number": 13,
                "title": "Unlinked issue",
                "body": "No decision marker",
                "html_url": "https://github.com/acme/demo/issues/13",
                "created_at": "2026-07-20T09:00:00Z",
                "updated_at": "2026-07-20T10:00:00Z",
            },
        ],
        "/repos/acme/demo/pulls": [
            {
                "number": 7,
                "title": "Resume onboarding on mobile",
                "body": (
                    "decision:onboarding-improvement-v1\n"
                    "Acceptance: users can resume onboarding on mobile\n"
                    "Test: mobile onboarding resume integration test\n"
                    "Risk: none identified"
                ),
                "html_url": "https://github.com/acme/demo/pull/7",
                "created_at": "2026-07-20T11:00:00Z",
                "updated_at": "2026-07-20T12:00:00Z",
                "head": {"sha": "head1234567890"},
            }
        ],
        "/repos/acme/demo/commits": [
            {
                "sha": "1111111234567890",
                "commit": {
                    "message": "Unlinked commit",
                    "committer": {"date": "2026-07-20T12:00:00Z"},
                },
                "html_url": "https://github.com/acme/demo/commit/1111111",
            }
        ],
        "/repos/acme/demo/pulls/7/files": [
            {"filename": "src/onboarding.py", "status": "modified", "additions": 8, "deletions": 2}
        ],
        "/repos/acme/demo/pulls/7/commits": [
            {
                "sha": commit_sha,
                "commit": {
                    "message": "Implement onboarding resume",
                    "committer": {"date": "2026-07-20T12:00:00Z"},
                },
                "html_url": f"https://github.com/acme/demo/commit/{commit_sha}",
            }
        ],
        "/repos/acme/demo/commits/head1234567890/check-runs": {
            "check_runs": [
                {
                    "name": "mobile onboarding resume",
                    "status": "completed",
                    "conclusion": "success",
                }
            ]
        },
    }
    transport = FakeTransport(responses)
    batch = GitHubReadOnlyAdapter(
        "github-test-token",
        api_base_url="https://github.test",
        transport=transport,
    ).collect_for_decision(_package(), owner="acme", repo="demo")

    assert [item.source_type for item in batch.work_items] == [
        "issue",
        "pull_request",
        "commit",
    ]
    assert len(batch.delivery_reports) == 1
    assert batch.delivery_reports[0].changed_areas == ["src/onboarding.py"]
    assert any("mobile onboarding resume" in test for test in batch.delivery_reports[0].tests)
    assert batch.unmatched_records == 2
    assert all(request[0] == "GET" for request in transport.requests)
    assert all(
        request[2]["Authorization"] == "Bearer github-test-token"
        for request in transport.requests
    )
    assert all("github-test-token" not in request[1] for request in transport.requests)
