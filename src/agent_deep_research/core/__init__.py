"""Core research engine, multi-source search, BM25 distiller, and cryptographic verifier."""

from .distiller import BM25Distiller, ContentDistiller, DistilledContent, ResearchPassage
from .engine import ResearchDossier, ResearchEngine, ResearchPlan
from .search import MultiSearchAdapter, SearchResult
from .verifier import EvidenceSnippet, FactLedger

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
]
