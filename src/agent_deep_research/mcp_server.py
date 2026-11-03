"""
Model Context Protocol (MCP) Server for agent-deep-research.
Provides native deep research tools to Claude Code, Cursor, Copilot, and Benni OS.
"""

from __future__ import annotations

import json
import sys
from typing import Any, Dict

from .core import ResearchEngine
from .search import MultiSearchAdapter
from .verifier import FactLedger


def run_stdio() -> None:
    """Runs standard Model Context Protocol (MCP) JSON-RPC 2.0 stdio server loop."""
    engine = ResearchEngine()

    while True:
        line = sys.stdin.readline()
        if not line:
            break

        line = line.strip()
        if not line:
            continue

        try:
            req = json.loads(line)
        except json.JSONDecodeError:
            continue

        req_id = req.get("id")
        method = req.get("method")
        params = req.get("params", {})

        if method == "initialize":
            resp = {
                "jsonrpc": "2.0",
                "id": req_id,
                "result": {
                    "protocolVersion": "2024-11-05",
                    "capabilities": {"tools": {}},
                    "serverInfo": {
                        "name": "agent-deep-research",
                        "version": "1.0.0",
                    },
                },
            }
            sys.stdout.write(json.dumps(resp) + "\n")
            sys.stdout.flush()

        elif method == "notifications/initialized":
            pass

        elif method == "tools/list":
            tools = [
                {
                    "name": "deep_research",
                    "description": "Conducts autonomous multi-source deep research on a topic, returning an evidence-backed markdown dossier with verified citations and SHA-256 provenance hashes.",
                    "inputSchema": {
                        "type": "object",
                        "properties": {
                            "topic": {
                                "type": "string",
                                "description": "The research question, technology, or topic to investigate deeply.",
                            },
                            "depth": {
                                "type": "integer",
                                "description": "Research depth (1 for rapid synthesis, 2 for comprehensive multi-perspective investigation).",
                                "default": 1,
                            },
                        },
                        "required": ["topic"],
                    },
                },
                {
                    "name": "quick_search",
                    "description": "Fast multi-source search across DuckDuckGo, Wikipedia, and ArXiv without recursive synthesis.",
                    "inputSchema": {
                        "type": "object",
                        "properties": {
                            "query": {
                                "type": "string",
                                "description": "Search query keywords.",
                            },
                            "limit": {
                                "type": "integer",
                                "description": "Maximum number of search results to return.",
                                "default": 5,
                            },
                        },
                        "required": ["query"],
                    },
                },
                {
                    "name": "verify_claim",
                    "description": "Verifies whether a factual assertion is cryptographically supported by a source evidence text.",
                    "inputSchema": {
                        "type": "object",
                        "properties": {
                            "claim": {
                                "type": "string",
                                "description": "The specific claim or statistic to verify.",
                            },
                            "source_evidence": {
                                "type": "string",
                                "description": "The raw source text or reference paragraph.",
                            },
                        },
                        "required": ["claim", "source_evidence"],
                    },
                },
            ]
            resp = {
                "jsonrpc": "2.0",
                "id": req_id,
                "result": {"tools": tools},
            }
            sys.stdout.write(json.dumps(resp) + "\n")
            sys.stdout.flush()

        elif method == "tools/call":
            name = params.get("name")
            args = params.get("arguments", {})

            try:
                if name == "deep_research":
                    topic = args.get("topic", "")
                    depth = int(args.get("depth", 1))
                    dossier = engine.research(topic=topic, depth=depth)
                    text_out = dossier.to_markdown()

                elif name == "quick_search":
                    query = args.get("query", "")
                    limit = int(args.get("limit", 5))
                    res = engine.search_adapter.search(query=query, limit=limit)
                    text_out = json.dumps([r.to_dict() for r in res], indent=2)

                elif name == "verify_claim":
                    claim = args.get("claim", "")
                    source = args.get("source_evidence", "")
                    ledger = FactLedger()
                    ledger.add_snippet(text=source, source_url="https://source.local", title="Provided Evidence")
                    verification = ledger.verify_claim(claim)
                    text_out = json.dumps(verification, indent=2)

                else:
                    text_out = f"Unknown tool: {name}"

                resp = {
                    "jsonrpc": "2.0",
                    "id": req_id,
                    "result": {
                        "content": [{"type": "text", "text": text_out}],
                    },
                }
            except Exception as e:
                resp = {
                    "jsonrpc": "2.0",
                    "id": req_id,
                    "error": {"code": -32000, "message": str(e)},
                }

            sys.stdout.write(json.dumps(resp) + "\n")
            sys.stdout.flush()

        elif method == "ping":
            resp = {"jsonrpc": "2.0", "id": req_id, "result": {}}
            sys.stdout.write(json.dumps(resp) + "\n")
            sys.stdout.flush()


if __name__ == "__main__":
    run_stdio()
