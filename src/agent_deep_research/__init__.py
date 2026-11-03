"""
agent-deep-research: Autonomous Multi-Source Deep Research & Evidence Synthesis Engine
Part of Benni Master OS v9.4 ecosystem.
"""

from .core import ResearchEngine, ResearchDossier, ResearchPlan
from .search import MultiSearchAdapter, SearchResult
from .distiller import ContentDistiller, DistilledContent
from .verifier import EvidenceSnippet, FactLedger

__version__ = "1.0.0"
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
    "EvidenceSnippet",
    "FactLedger",
    "__version__",
]
