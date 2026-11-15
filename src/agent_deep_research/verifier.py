"""Backwards-compatible shim for agent_deep_research.core.verifier."""

from .core.verifier import EvidenceSnippet, FactLedger

__all__ = ["EvidenceSnippet", "FactLedger"]
