"""Backwards-compatible shim for agent_deep_research.core.distiller."""

from .core.distiller import (
    BM25Distiller,
    ContentDistiller,
    DistilledContent,
    ResearchPassage,
)

__all__ = [
    "ContentDistiller",
    "DistilledContent",
    "BM25Distiller",
    "ResearchPassage",
]
