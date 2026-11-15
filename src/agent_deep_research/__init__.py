"""
agent-deep-research: Autonomous Multi-Source Deep Research & Evidence Synthesis Engine
Part of Benni Master OS v9.4 ecosystem.
"""

from .core import (
    BM25Distiller,
    ContentDistiller,
    DistilledContent,
    EvidenceSnippet,
    FactLedger,
    MultiSearchAdapter,
    ResearchDossier,
    ResearchEngine,
    ResearchPassage,
    ResearchPlan,
    SearchResult,
)
from .serve import HealthMonitor, HealthSnapshot, ResearchTelemetry
from .tools import BenchmarkMatrix, DoctorReport, MatrixRow, ResearchDoctor

__version__ = "1.1.0"
__author__ = "Benni Alencar"
__email__ = "bennialencar@gmail.com"
__all__ = [
    "ResearchEngine",
    "ResearchDossier",
    "ResearchPlan",
    "MultiSearchAdapter",
    "SearchResult",
    "ContentDistiller",
    "DistilledContent",
    "BM25Distiller",
    "ResearchPassage",
    "EvidenceSnippet",
    "FactLedger",
    "HealthMonitor",
    "HealthSnapshot",
    "ResearchTelemetry",
    "ResearchDoctor",
    "DoctorReport",
    "BenchmarkMatrix",
    "MatrixRow",
    "__version__",
]
