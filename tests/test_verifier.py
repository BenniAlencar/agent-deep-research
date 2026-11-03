import pytest
from agent_deep_research.verifier import EvidenceSnippet, FactLedger


def test_evidence_snippet_hash_integrity():
    snip = EvidenceSnippet(
        text="Majorana zero modes demonstrate non-Abelian statistics.",
        source_url="https://arxiv.org/abs/2601.12345",
        title="Topological Quantum Computing",
    )
    assert snip.sha256_hash != ""
    assert snip.verify_integrity() is True

    # Tamper text
    snip.text = "Tampered text without updating hash"
    assert snip.verify_integrity() is False


def test_fact_ledger_addition_and_bibliography():
    ledger = FactLedger()
    ref1 = ledger.add_snippet("Quantum supremacy via Gaussian Boson Sampling.", "https://nature.com/q1", "Nature Article 1")
    ref2 = ledger.add_snippet("Fault tolerance threshold achieved under 0.5% error rate.", "https://science.org/q2", "Science Article 2")

    assert ref1 == "REF-1"
    assert ref2 == "REF-2"
    assert len(ledger.snippets) == 2

    root_hash = ledger.compute_root_hash()
    assert len(root_hash) == 64

    bib = ledger.format_bibliography_markdown()
    assert "[REF-1]" in bib
    assert "[REF-2]" in bib
    assert "https://nature.com/q1" in bib
    assert root_hash in bib


def test_claim_verification():
    ledger = FactLedger()
    ledger.add_snippet(
        text="The dual-engine architecture delivers sub-15ms response latency with 99.8% cache hit rate.",
        source_url="https://benchmark.local/report",
        title="Benchmark 2026",
    )

    # Valid supported claim
    res = ledger.verify_claim("sub-15ms response latency with 99.8% cache hit rate")
    assert res["verified"] is True
    assert res["match_ref"] == "REF-1"
    assert res["confidence"] > 0.6
    assert res["evidence_hash"] is not None

    # Unsupported claim
    res2 = ledger.verify_claim("astronomers discovered extraterrestrial radio signals from Alpha Centauri")
    assert res2["verified"] is False
    assert res2["match_ref"] is None
