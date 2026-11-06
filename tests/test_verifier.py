import pytest
from agent_deep_research.verifier import EvidenceSnippet, FactLedger
from agent_deep_research.distiller import BM25Distiller


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

    # Valid supported claim with numbers
    res = ledger.verify_claim("sub-15ms response latency with 99.8% cache hit rate")
    assert res["verified"] is True
    assert res["match_ref"] == "REF-1"
    assert res["confidence"] > 0.6
    assert res["evidence_hash"] is not None

    # Unsupported claim
    res2 = ledger.verify_claim("astronomers discovered extraterrestrial radio signals from Alpha Centauri")
    assert res2["verified"] is False
    assert res2["match_ref"] is None


def test_numerical_contradiction_blocking():
    """
    Validates that a numerical contradiction (e.g. $49.9B vs $94.9B) is rejected
    even if high-frequency surrounding words (revenue, apple, announced) overlap heavily.
    """
    passage = "Apple announced $94.9B revenue for Q4 2024 with record iPhone sales."
    
    # False claim with hallucinated number
    false_claim = "Apple announced $49.9B revenue for Q4 2024"
    assert FactLedger.verify_citation(false_claim, passage) is False

    # True claim with exact number
    true_claim = "Apple announced $94.9B revenue for Q4 2024"
    assert FactLedger.verify_citation(true_claim, passage) is True

    # Ledger level test
    ledger = FactLedger()
    ledger.add_snippet(passage, "https://sec.gov/10k", "Apple 10-K")

    res_false = ledger.verify_claim(false_claim)
    assert res_false["verified"] is False

    res_true = ledger.verify_claim(true_claim)
    assert res_true["verified"] is True


def test_verbatim_quote_enforcement():
    passage = "Autonomous agents require verifiable cryptographic state ledgers to eliminate context drift."
    
    # Valid quote
    assert FactLedger.verify_citation(
        claim="Agents need state ledgers",
        passage_text=passage,
        threshold=0.2,
        exact_quote="verifiable cryptographic state ledgers"
    ) is True

    # Invalid quote (hallucinated quote)
    assert FactLedger.verify_citation(
        claim="Agents need state ledgers",
        passage_text=passage,
        threshold=0.2,
        exact_quote="unconstrained autonomous free rein"
    ) is False


def test_bm25_distiller_reindex_reset():
    """
    Ensures that calling index_documents a second time completely wipes
    corpus, inverted_index, and document frequencies rather than accumulating them.
    """
    distiller = BM25Distiller()
    docs1 = [("https://source1.com", "First run documents detailing quantum computing and qubits.")]
    distiller.index_documents(docs1)
    
    assert len(distiller.corpus) == 1
    assert "qubits" in distiller.inverted_index
    
    # Second indexing run with completely different content
    docs2 = [("https://source2.com", "Second run documents analyzing distributed consensus in Raft clusters.")]
    distiller.index_documents(docs2)
    
    assert len(distiller.corpus) == 1
    assert "qubits" not in distiller.inverted_index
    assert "raft" in distiller.inverted_index
    assert distiller.corpus[0].source_url == "https://source2.com"
