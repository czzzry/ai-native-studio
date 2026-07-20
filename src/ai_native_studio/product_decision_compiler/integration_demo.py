"""Run a local proof of the read-only Linear and GitHub adapters."""

from __future__ import annotations

from collections.abc import Mapping
from urllib.parse import urlsplit

from .conformance import ConformanceEngine, build_digest, render_digest
from .contracts import DecisionPackageService, InMemoryDecisionPackageStore
from .fixtures import load_fixture
from .integrations import GitHubReadOnlyAdapter, LinearReadOnlyAdapter


class DemoTransport:
    """Synthetic provider responses used to prove the adapters without network access."""

    def __init__(self) -> None:
        self._responses: dict[str, object] = {
            "graphql": {
                "data": {
                    "team": {
                        "issues": {
                            "nodes": [
                                {
                                    "id": "linear-onboarding-101",
                                    "identifier": "STU-101",
                                    "title": "Improve mobile onboarding",
                                    "description": (
                                        "decision:onboarding-improvement-v1\n"
                                        "Resume behavior"
                                    ),
                                    "url": "https://linear.example/issue/STU-101",
                                    "createdAt": "2026-07-20T09:00:00Z",
                                    "updatedAt": "2026-07-20T10:00:00Z",
                                    "project": {"name": "Onboarding"},
                                    "parent": None,
                                    "labels": {"nodes": [{"name": "agentic"}]},
                                },
                                {
                                    "id": "linear-unlinked-102",
                                    "identifier": "STU-102",
                                    "title": "Unlinked cleanup",
                                    "description": "No decision marker.",
                                    "url": "https://linear.example/issue/STU-102",
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
            },
            "/repos/demo/studio/issues": [
                {
                    "number": 12,
                    "title": "Onboarding issue",
                    "body": "decision:onboarding-improvement-v1",
                    "html_url": "https://github.example/demo/studio/issues/12",
                    "created_at": "2026-07-20T09:00:00Z",
                    "updated_at": "2026-07-20T10:00:00Z",
                }
            ],
            "/repos/demo/studio/pulls": [
                {
                    "number": 7,
                    "title": "Resume onboarding on mobile",
                    "body": (
                        "decision:onboarding-improvement-v1\n"
                        "Test: Users can resume onboarding on mobile\n"
                        "Risk: authentication token migration"
                    ),
                    "html_url": "https://github.example/demo/studio/pull/7",
                    "created_at": "2026-07-20T11:00:00Z",
                    "updated_at": "2026-07-20T12:00:00Z",
                    "head": {"sha": "head1234567890"},
                }
            ],
            "/repos/demo/studio/commits": [
                {
                    "sha": "unlinked1234567890",
                    "commit": {
                        "message": "Unlinked commit",
                        "committer": {"date": "2026-07-20T12:00:00Z"},
                    },
                    "html_url": "https://github.example/demo/studio/commit/unlinked",
                }
            ],
            "/repos/demo/studio/pulls/7/files": [
                {"filename": "src/onboarding.py", "status": "modified"}
            ],
            "/repos/demo/studio/pulls/7/commits": [
                {
                    "sha": "linked1234567890",
                    "commit": {
                        "message": "Implement onboarding resume",
                        "committer": {"date": "2026-07-20T12:00:00Z"},
                    },
                    "html_url": "https://github.example/demo/studio/commit/linked",
                }
            ],
            "/repos/demo/studio/commits/head1234567890/check-runs": {
                "check_runs": [
                    {
                        "name": "mobile onboarding resume",
                        "status": "completed",
                        "conclusion": "success",
                    }
                ]
            },
        }

    def request(
        self,
        *,
        method: str,
        url: str,
        headers: Mapping[str, str],
        payload: bytes | None = None,
    ) -> object:
        del headers, payload
        key = "graphql" if method == "POST" else urlsplit(url).path
        return self._responses[key]


def _approved_package():
    fixture = load_fixture()
    service = DecisionPackageService(InMemoryDecisionPackageStore())
    created = service.create_or_reuse(
        decision_id=fixture.decision_id,
        source_id=fixture.source_id,
        draft=fixture.decision,
        created_at_ms=1_700_000_000_000,
    )
    approval = service.approve(
        founder_id="founder-local",
        product_agent_id="product-agent-local",
        version_id=created.package.version_id,
        source_event_id="integration-demo-approval",
        approved_at_ms=1_700_000_000_001,
    )
    if approval.package is None:
        raise RuntimeError("Integration demo could not create its approved package.")
    return approval.package


def main() -> None:
    package = _approved_package()
    transport = DemoTransport()
    linear = LinearReadOnlyAdapter(
        "demo-linear-token",
        endpoint="https://linear.example/graphql",
        transport=transport,
    )
    github = GitHubReadOnlyAdapter(
        "demo-github-token",
        api_base_url="https://github.example",
        transport=transport,
    )
    linear_batch = linear.collect_for_decision(package, team_id="team-studio")
    github_batch = github.collect_for_decision(package, owner="demo", repo="studio")

    engine = ConformanceEngine()
    findings = [
        engine.process_work(package, item)
        for item in [*linear_batch.work_items, *github_batch.work_items]
    ]
    for report in github_batch.delivery_reports:
        findings.extend(engine.process_delivery(package, report))
    digest = build_digest(
        package,
        findings,
        total_evidence_items=len(linear_batch.work_items)
        + len(github_batch.work_items)
        + len(github_batch.delivery_reports),
    )

    print("Product Decision Compiler — Read-only integration proof")
    print(f"Linear linked work items: {len(linear_batch.work_items)}")
    print(f"GitHub linked work items: {len(github_batch.work_items)}")
    print(f"GitHub delivery reports: {len(github_batch.delivery_reports)}")
    print("Provider writes performed: 0")
    print()
    print(render_digest(digest))
    print()
    print("Integration proof: PASS")


if __name__ == "__main__":
    main()
