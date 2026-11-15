"""
Runtime health monitor for agent-deep-research.
Validates BM25 distiller, SHA-256 FactLedger integrity, and offline mock search readiness.
"""

from __future__ import annotations

import platform
import time
from dataclasses import dataclass
from typing import Any, Dict

from ..core.distiller import ContentDistiller
from ..core.search import MultiSearchAdapter, SearchResult
from ..core.verifier import FactLedger


@dataclass
class HealthSnapshot:
    status: str  # "healthy" | "degraded" | "unhealthy"
    python_version: str
    platform_system: str
    distiller_ok: bool
    ledger_ok: bool
    search_mock_ok: bool
    check_latency_ms: float

    def to_dict(self) -> Dict[str, Any]:
        return {
            "status": self.status,
            "python_version": self.python_version,
            "platform_system": self.platform_system,
            "distiller_ok": self.distiller_ok,
            "ledger_ok": self.ledger_ok,
            "search_mock_ok": self.search_mock_ok,
            "check_latency_ms": round(self.check_latency_ms, 3),
        }


class HealthMonitor:
    """Performs lightweight runtime health checks for the research subsystem."""

    def check(self) -> HealthSnapshot:
        t0 = time.perf_counter()

        distiller_ok = False
        try:
            d = ContentDistiller()
            sample = (
                "<p>Topological quantum computation utilizes non-Abelian anyons and Majorana zero modes "
                "to store quantum information non-locally with fault-tolerant braiding operations.</p>"
            )
            res = d.distill(sample, query="topological quantum majorana")
            distiller_ok = len(res.chunks) > 0
        except Exception:
            distiller_ok = False

        ledger_ok = False
        try:
            ledger = FactLedger()
            ref_id = ledger.add_snippet("Surface code threshold is 0.7%.", "https://example.org/qec", "QEC")
            snip = ledger.get_snippet(ref_id)
            ver = ledger.verify_claim("Surface code threshold is 0.7%")
            ledger_ok = (snip is not None and bool(snip.sha256_hash)) and bool(ver.get("verified"))
        except Exception:
            ledger_ok = False

        search_mock_ok = False
        try:
            adapter = MultiSearchAdapter()
            mocks = [
                SearchResult("QEC Overview", "https://example.org/qec", "Surface code threshold is 0.7%.", "mock", 0.99)
            ]
            results = adapter.search("quantum error correction", limit=2, mock_results=mocks)
            search_mock_ok = len(results) == 1
        except Exception:
            search_mock_ok = False

        status = "healthy" if (distiller_ok and ledger_ok and search_mock_ok) else "unhealthy"
        elapsed_ms = (time.perf_counter() - t0) * 1000.0
        return HealthSnapshot(
            status=status,
            python_version=platform.python_version(),
            platform_system=f"{platform.system()} {platform.release()}",
            distiller_ok=distiller_ok,
            ledger_ok=ledger_ok,
            search_mock_ok=search_mock_ok,
            check_latency_ms=elapsed_ms,
        )
