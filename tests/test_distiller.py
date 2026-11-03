import pytest
from agent_deep_research.distiller import ContentDistiller


def test_clean_html_strips_scripts_and_tags():
    distiller = ContentDistiller()
    raw = """
    <html>
        <head><script>alert('malicious')</script><style>body { color: red; }</style></head>
        <nav><a href="/terms">Terms</a></nav>
        <body>
            <h1>Groundbreaking Finding</h1>
            <p>This is substantive factual text that should be kept intact &amp; clean.</p>
            <footer>Copyright 2026</footer>
        </body>
    </html>
    """
    cleaned = distiller.clean_html(raw)
    assert "alert" not in cleaned
    assert "body { color" not in cleaned
    assert "Terms" not in cleaned
    assert "Copyright" not in cleaned
    assert "Groundbreaking Finding" in cleaned
    assert "substantive factual text" in cleaned


def test_distiller_compression_and_bm25_selection():
    distiller = ContentDistiller()
    noisy_document = """
    <p>Cookie policy: We use cookies to improve user experience. Click accept to proceed.</p>
    <p>Sign in to your account or subscribe to our newsletter for daily updates.</p>
    <p>Topological insulators exhibit conducting edge states protected by time-reversal symmetry.</p>
    <p>Share on Twitter, Facebook, LinkedIn, or Pinterest right now!</p>
    <p>Quantum spin Hall effect was observed in bismuth selenide thin films at room temperature.</p>
    <p>Leave a comment below to join the discussion on our tech blog.</p>
    """ * 10

    res = distiller.distill(
        raw_content=noisy_document,
        query="topological insulators quantum spin hall effect bismuth",
        title="Physics Review",
        source_url="https://physics.org/art1",
        max_chunks=2,
    )

    assert res.compression_ratio > 0.5
    assert len(res.chunks) <= 2
    assert res.estimated_tokens_saved > 0
    # Relevant chunks are prioritized
    found_relevant = any("topological insulators" in c.lower() or "quantum spin" in c.lower() for c in res.chunks)
    assert found_relevant is True


def test_distiller_empty_or_minimal_fallback():
    distiller = ContentDistiller()
    res = distiller.distill("", query="anything")
    assert res.compression_ratio == 0.0
    assert len(res.chunks) == 0
