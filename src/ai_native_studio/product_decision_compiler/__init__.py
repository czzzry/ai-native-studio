"""Offline Product Decision Compiler alignment proof."""

from .compiler import DecisionCompilationError, DeterministicIntentCompiler
from .conformance import ConformanceEngine, ConformanceEvaluator, build_digest
from .contracts import (
    DecisionPackage,
    DecisionPackageDraft,
    DecisionPackageService,
    DeliveryReport,
    WorkItemEvidence,
)
from .integrations import (
    DecisionBinding,
    DecisionReference,
    GitHubReadOnlyAdapter,
    IntegrationEvidenceBatch,
    LinearReadOnlyAdapter,
    ReadOnlyIntegrationError,
    extract_decision_reference,
)

__all__ = [
    "ConformanceEngine",
    "ConformanceEvaluator",
    "DecisionCompilationError",
    "DecisionPackage",
    "DecisionPackageDraft",
    "DecisionPackageService",
    "DecisionBinding",
    "DecisionReference",
    "DeterministicIntentCompiler",
    "DeliveryReport",
    "GitHubReadOnlyAdapter",
    "IntegrationEvidenceBatch",
    "LinearReadOnlyAdapter",
    "ReadOnlyIntegrationError",
    "WorkItemEvidence",
    "build_digest",
    "extract_decision_reference",
]
