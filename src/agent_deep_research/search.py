"""Backwards-compatible shim for agent_deep_research.core.search."""

from .core.search import MultiSearchAdapter, SearchResult

__all__ = ["MultiSearchAdapter", "SearchResult"]
