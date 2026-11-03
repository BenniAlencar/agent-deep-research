import pytest
from agent_deep_research.core import ResearchEngine, ResearchPlan, ResearchDossier


def test_research_plan_generation():
    engine = ResearchEngine()
    plan1 = engine.generate_plan("Autonomous Multi-Agent Routing", depth=1)
    assert plan1.topic == "Autonomous Multi-Agent Routing"
    assert len(plan1.sub_hypotheses) == 2

    plan2 = engine.generate_plan("Autonomous Multi-Agent Routing", depth=2)
    assert len(plan2.sub_hypotheses) == 4


def test_research_engine_execution_with_mock_evidence():
    engine = ResearchEngine()
    mock_corpus = [
        {
            "title": "Agent Routing Protocol V3",
            "url": "https://specs.benni.org/routing",
            "text": "The router deploys an inverted index with graph centrality measures to dispatch sub-tasks in O(1) latency. Verified across 10,000 synthetic trials with 99.9% dispatch success."
        },
        {
            "title": "Distributed Consensus in Multi-Agent Swarms",
            "url": "https://research.benni.org/consensus",
            "text": "By adopting Paxos-derived raft states, the swarm achieves Byzantine fault tolerance up to f=(n-1)/3 nodes without network partitioning deadlocks."
        }
    ]

    dossier = engine.research(
        topic="Multi-Agent Routing and Consensus",
        depth=1,
        mock_evidence=mock_corpus,
    )

    assert isinstance(dossier, ResearchDossier)
    assert dossier.sources_count == 2
    assert dossier.root_evidence_hash != ""
    assert len(dossier.key_findings) == 4
    assert len(dossier.sections) == 3

    md = dossier.to_markdown()
    assert "# Autonomous Deep Research Dossier" in md
    assert "Multi-Agent Routing and Consensus" in md
    assert "[REF-1]" in md
    assert "https://specs.benni.org/routing" in md
    assert dossier.root_evidence_hash in md

    # Check serialization
    d = dossier.to_dict()
    assert d["topic"] == "Multi-Agent Routing and Consensus"
    assert "root_evidence_hash" in d


def test_research_dossier_markdown_and_dict():
    engine = ResearchEngine()
    plan = engine.generate_plan("AI Agent Governance")
    assert "architecture mechanism" in plan.sub_hypotheses[0]
    d = plan.to_dict()
    assert d["depth"] == 1
