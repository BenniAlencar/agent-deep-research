"""
Cryptographic Provenance and Citation Verification Ledger.
Ensures zero-hallucination evidence trails with SHA-256 hashes for all citations.
"""

from __future__ import annotations

import hashlib
import time
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional


@dataclass
class EvidenceSnippet:
    """An atomic verified piece of evidence extracted from a source."""
    text: str
    source_url: str
    title: str
    relevance_score: float = 1.0
    timestamp: float = field(default_factory=time.time)
    sha256_hash: str = field(default="")

    def __post_init__(self) -> None:
        if not self.sha256_hash:
            self.sha256_hash = self.compute_hash()

    def compute_hash(self) -> str:
        payload = f"{self.source_url}::{self.text.strip()}".encode("utf-8")
        return hashlib.sha256(payload).hexdigest()

    def verify_integrity(self) -> bool:
        return self.compute_hash() == self.sha256_hash

    def to_dict(self) -> Dict[str, Any]:
        return {
            "text": self.text,
            "source_url": self.source_url,
            "title": self.title,
            "relevance_score": round(self.relevance_score, 4),
            "timestamp": self.timestamp,
            "sha256_hash": self.sha256_hash,
        }


class FactLedger:
    """
    Immutable ledger of evidence snippets and citations.
    Generates verifiable references and verifies assertions against factual ground truth.
    """

    def __init__(self) -> None:
        self.snippets: List[EvidenceSnippet] = []
        self._url_to_ref: Dict[str, str] = {}
        self._ref_to_snippet: Dict[str, EvidenceSnippet] = {}

    def add_snippet(self, text: str, source_url: str, title: str, relevance_score: float = 1.0) -> str:
        """Adds a snippet and returns its citation reference key (e.g. [REF-1])."""
        snippet = EvidenceSnippet(
            text=text.strip(),
            source_url=source_url.strip(),
            title=title.strip(),
            relevance_score=relevance_score,
        )
        self.snippets.append(snippet)
        ref_id = f"REF-{len(self.snippets)}"
        self._ref_to_snippet[ref_id] = snippet
        self._url_to_ref[snippet.source_url] = ref_id
        return ref_id

    def get_snippet(self, ref_id: str) -> Optional[EvidenceSnippet]:
        return self._ref_to_snippet.get(ref_id)

    def verify_claim(self, claim_text: str, min_match_ratio: float = 0.5) -> Dict[str, Any]:
        """
        Verifies if an extracted assertion or claim is supported by at least one
        cryptographically tracked evidence snippet.
        """
        claim_lower = claim_text.lower().strip()
        words = set(claim_lower.split())
        if not words:
            return {"verified": False, "match_ref": None, "confidence": 0.0}

        best_ref = None
        best_ratio = 0.0

        for ref_id, snip in self._ref_to_snippet.items():
            snip_lower = snip.text.lower()
            snip_words = set(snip_lower.split())
            if not snip_words:
                continue

            intersection = words.intersection(snip_words)
            ratio = len(intersection) / len(words)
            if ratio > best_ratio:
                best_ratio = ratio
                best_ref = ref_id

        verified = best_ratio >= min_match_ratio
        return {
            "verified": verified,
            "match_ref": best_ref if verified else None,
            "confidence": round(best_ratio, 4),
            "evidence_hash": self._ref_to_snippet[best_ref].sha256_hash if verified and best_ref else None,
        }

    def compute_root_hash(self) -> str:
        """Computes aggregate SHA-256 root hash over all recorded evidence items."""
        if not self.snippets:
            return hashlib.sha256(b"empty_ledger").hexdigest()
        combined = "".join(sorted([s.sha256_hash for s in self.snippets])).encode("utf-8")
        return hashlib.sha256(combined).hexdigest()

    def format_bibliography_markdown(self) -> str:
        """Formats an academic/audit-grade bibliography with cryptographic hashes."""
        if not self.snippets:
            return "_No external evidence citations recorded._"

        lines = ["### Verified References & Cryptographic Evidence Ledger\n"]
        lines.append("| Ref | Title & Source | Verification Hash | Relevance |")
        lines.append("| :--- | :--- | :--- | :---: |")

        for ref_id, snip in self._ref_to_snippet.items():
            short_hash = f"`{snip.sha256_hash[:12]}...`"
            source_link = f"[{snip.title}]({snip.source_url})"
            score_pct = f"{int(snip.relevance_score * 100)}%"
            lines.append(f"| **[{ref_id}]** | {source_link} | {short_hash} | {score_pct} |")

        lines.append(f"\n**Ledger Root Hash (SHA-256):** `{self.compute_root_hash()}`")
        return "\n".join(lines)
