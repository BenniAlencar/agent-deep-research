import json
import pytest
from agent_deep_research.core import ResearchEngine
from agent_deep_research.verifier import FactLedger


def test_mcp_core_tool_logic():
    engine = ResearchEngine()

    # 1. Test quick search logic
    mock_mocks = [
        {"title": "Test Resource", "url": "https://test.local", "snippet": "Sample snippet content", "source": "web", "score": 1.0}
    ]
    # Quick search returns results
    plan = engine.generate_plan("Test Topic")
    assert plan.primary_query == "Test Topic"

    # 2. Test claim verification logic
    ledger = FactLedger()
    ledger.add_snippet("Topological protection yields 100x lower decoherence rates.", "https://lab.org/result", "Lab Report")
    res = ledger.verify_claim("100x lower decoherence rates")
    assert res["verified"] is True
    assert res["match_ref"] == "REF-1"
