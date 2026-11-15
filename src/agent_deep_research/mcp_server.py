"""Backwards-compatible shim for agent_deep_research.serve.mcp_bridge."""

from .serve.mcp_bridge import run_stdio

__all__ = ["run_stdio"]
