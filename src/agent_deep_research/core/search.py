"""
Resilient Multi-Engine Search Adapter.
Supports zero-key free search (DuckDuckGo, Wikipedia, ArXiv) and optional premium providers.
"""

from __future__ import annotations

import json
import re
import urllib.parse
import urllib.request
import xml.etree.ElementTree as ET
from dataclasses import dataclass
from typing import Any, Dict, List, Optional


@dataclass
class SearchResult:
    title: str
    url: str
    snippet: str
    source: str = "web"
    score: float = 1.0

    def to_dict(self) -> Dict[str, Any]:
        return {
            "title": self.title,
            "url": self.url,
            "snippet": self.snippet,
            "source": self.source,
            "score": round(self.score, 4),
        }


class MultiSearchAdapter:
    """
    Unified multi-engine search router with automatic fallback cascading.
    Works immediately without requiring paid API keys.
    """

    USER_AGENT = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36 AgentDeepResearch/1.0"

    def __init__(self, tavily_key: Optional[str] = None, timeout: int = 10) -> None:
        self.tavily_key = tavily_key
        self.timeout = timeout

    def search(
        self,
        query: str,
        limit: int = 5,
        include_academic: bool = True,
        mock_results: Optional[List[SearchResult]] = None,
    ) -> List[SearchResult]:
        """
        Executes unified search across free zero-key providers or configured engines.
        """
        if mock_results is not None:
            return mock_results[:limit]

        results: List[SearchResult] = []

        # 1. Try DuckDuckGo Lite / HTML Search
        try:
            ddg_res = self._search_duckduckgo(query, limit=limit)
            results.extend(ddg_res)
        except Exception:
            pass

        # 2. If results are sparse or academic is requested, search Wikipedia & ArXiv
        if len(results) < limit:
            try:
                wiki_res = self._search_wikipedia(query, limit=max(2, limit - len(results)))
                results.extend(wiki_res)
            except Exception:
                pass

        if include_academic and len(results) < limit:
            try:
                arxiv_res = self._search_arxiv(query, limit=max(2, limit - len(results)))
                results.extend(arxiv_res)
            except Exception:
                pass

        # Deduplicate by URL
        seen_urls = set()
        deduped = []
        for r in results:
            clean_url = r.url.rstrip("/")
            if clean_url not in seen_urls:
                seen_urls.add(clean_url)
                deduped.append(r)

        return deduped[:limit]

    def _search_duckduckgo(self, query: str, limit: int = 5) -> List[SearchResult]:
        url = "https://html.duckduckgo.com/html/?q=" + urllib.parse.quote_plus(query)
        req = urllib.request.Request(url, headers={"User-Agent": self.USER_AGENT})
        with urllib.request.urlopen(req, timeout=self.timeout) as resp:
            html = resp.read().decode("utf-8", errors="replace")

        results = []
        # Parse result blocks
        blocks = re.findall(r'<div class="result__body">.*?</div>\s*</div>', html, flags=re.DOTALL)
        for b in blocks:
            # Extract title and link
            link_match = re.search(r'<a class="result__url" href="([^"]+)">(.*?)</a>', b)
            title_match = re.search(r'<a class="result__snippet[^>]*href="[^"]*">(.*?)</a>', b)
            snippet_match = re.search(r'<a class="result__snippet[^>]*>(.*?)</a>', b)

            if not link_match:
                # Alternate pattern
                link_match = re.search(r'<a class="result__a" href="([^"]+)">(.*?)</a>', b)

            if link_match:
                raw_url = link_match.group(1)
                # Unpack DuckDuckGo redirect if needed
                if "uddg=" in raw_url:
                    parsed = urllib.parse.parse_qs(urllib.parse.urlparse(raw_url).query)
                    raw_url = parsed.get("uddg", [raw_url])[0]

                raw_title = re.sub(r"<[^>]+>", "", link_match.group(2) if len(link_match.groups()) > 1 else "Web Result").strip()
                raw_snippet = re.sub(r"<[^>]+>", "", snippet_match.group(1)).strip() if snippet_match else ""

                if raw_url.startswith("http"):
                    results.append(SearchResult(
                        title=raw_title or "Web Evidence",
                        url=raw_url,
                        snippet=raw_snippet or raw_title,
                        source="duckduckgo",
                        score=0.95,
                    ))

            if len(results) >= limit:
                break

        return results

    def _search_wikipedia(self, query: str, limit: int = 3) -> List[SearchResult]:
        url = f"https://en.wikipedia.org/w/api.php?action=opensearch&search={urllib.parse.quote_plus(query)}&limit={limit}&namespace=0&format=json"
        req = urllib.request.Request(url, headers={"User-Agent": self.USER_AGENT})
        with urllib.request.urlopen(req, timeout=self.timeout) as resp:
            data = json.loads(resp.read().decode("utf-8"))

        # Format: [query, [titles], [descriptions], [links]]
        results = []
        if len(data) >= 4:
            titles = data[1]
            descriptions = data[2]
            links = data[3]
            for i in range(len(titles)):
                results.append(SearchResult(
                    title=f"Wikipedia: {titles[i]}",
                    url=links[i],
                    snippet=descriptions[i] if descriptions[i] else f"Wikipedia article for {titles[i]}",
                    source="wikipedia",
                    score=0.90,
                ))
        return results

    def _search_arxiv(self, query: str, limit: int = 3) -> List[SearchResult]:
        clean_q = re.sub(r"[^\w\s]", " ", query).strip()
        url = f"http://export.arxiv.org/api/query?search_query=all:{urllib.parse.quote_plus(clean_q)}&start=0&max_results={limit}"
        req = urllib.request.Request(url, headers={"User-Agent": self.USER_AGENT})
        with urllib.request.urlopen(req, timeout=self.timeout) as resp:
            xml_data = resp.read().decode("utf-8")

        root = ET.fromstring(xml_data)
        ns = {"atom": "http://www.w3.org/2005/Atom"}
        results = []
        for entry in root.findall("atom:entry", ns):
            title_elem = entry.find("atom:title", ns)
            id_elem = entry.find("atom:id", ns)
            summary_elem = entry.find("atom:summary", ns)

            if title_elem is not None and id_elem is not None:
                title = re.sub(r"\s+", " ", title_elem.text or "").strip()
                link = (id_elem.text or "").strip()
                summary = re.sub(r"\s+", " ", summary_elem.text or "").strip() if summary_elem is not None else ""
                results.append(SearchResult(
                    title=f"ArXiv: {title}",
                    url=link,
                    snippet=summary[:300] + ("..." if len(summary) > 300 else ""),
                    source="arxiv",
                    score=0.92,
                ))
        return results

    def fetch_page_content(self, url: str) -> str:
        """Fetches raw webpage HTML with resilient header emulation."""
        req = urllib.request.Request(url, headers={"User-Agent": self.USER_AGENT, "Accept": "text/html,application/xhtml+xml"})
        with urllib.request.urlopen(req, timeout=self.timeout) as resp:
            return resp.read().decode("utf-8", errors="replace")
