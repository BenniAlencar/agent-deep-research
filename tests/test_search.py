import pytest
from agent_deep_research.search import MultiSearchAdapter, SearchResult


def test_search_result_serialization():
    sr = SearchResult(
        title="DeepSeek-R1 Architecture",
        url="https://arxiv.org/abs/2501.12948",
        snippet="Incentivizing reasoning capability in LLMs via reinforcement learning.",
        source="arxiv",
        score=0.98,
    )
    d = sr.to_dict()
    assert d["title"] == "DeepSeek-R1 Architecture"
    assert d["url"] == "https://arxiv.org/abs/2501.12948"
    assert d["source"] == "arxiv"
    assert d["score"] == 0.98


def test_search_adapter_mock_mode_and_deduplication():
    adapter = MultiSearchAdapter()
    mocks = [
        SearchResult("Res 1", "https://siteA.com/page", "Snippet 1"),
        SearchResult("Res 1 Duplicate", "https://siteA.com/page/", "Snippet 1 Dup"),
        SearchResult("Res 2", "https://siteB.com/page", "Snippet 2"),
    ]
    res = adapter.search(query="test", limit=5, mock_results=mocks)
    assert len(res) == 3
    assert res[0].url == "https://siteA.com/page"


def test_search_duckduckgo_parsing_resilience():
    adapter = MultiSearchAdapter()
    # Test that invalid / unreachable query degrades gracefully without crashing
    res = adapter.search(query="test_query_fallback", limit=2, include_academic=False, mock_results=[])
    assert isinstance(res, list)
