from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]


def test_evidence_review_uses_the_integration_proof_scenario() -> None:
    """Keep the public review grounded in the runnable integration proof."""
    review = (ROOT / "docs" / "demo" / "index.html").read_text(encoding="utf-8")
    integration_demo = (
        ROOT
        / "src"
        / "ai_native_studio"
        / "product_decision_compiler"
        / "integration_demo.py"
    ).read_text(encoding="utf-8")

    for evidence in (
        "decision:onboarding-improvement-v1",
        "STU-101",
        "Resume onboarding on mobile",
        "authentication token migration",
        "linked123",
    ):
        assert evidence in review
        assert evidence in integration_demo

    assert "Provider writes performed: 0" in integration_demo
    assert "applyFilter();" in review
