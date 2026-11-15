"""
Diagnostic probe (doctor) for agent-deep-research.
Validates BM25 distillation, SHA-256 FactLedger provenance, and offline research pipeline.
"""

from __future__ import annotations

import platform
import time
from dataclasses import dataclass, field
from typing import Any, Dict, List

from ..core.distiller import ContentDistiller
from ..core.engine import ResearchEngine
from ..core.search import SearchResult
from ..core.verifier import FactLedger
from ..serve.health_monitor import HealthMonitor


@dataclass
class ProbeCheck:
    name: str
    passed: bool
    latency_ms: float
    detail: str


@dataclass
class DoctorReport:
    overall_ok: bool
    python_version: str
    platform_info: str
    checks: List[ProbeCheck] = field(default_factory=list)
    total_latency_ms: float = 0.0

    def to_dict(self) -> Dict[str, Any]:
        return {
            "overall_ok": self.overall_ok,
            "python_version": self.python_version,
            "platform": self.platform_info,
            "total_latency_ms": round(self.total_latency_ms, 3),
            "checks": [
                {
                    "name": c.name,
                    "passed": c.passed,
                    "latency_ms": round(c.latency_ms, 3),
                    "detail": c.detail,
                }
                for c in self.checks
            ],
        }

    def format_report(self) -> str:
        lines = [
            f"agent-deep-research doctor | Python {self.python_version} | {self.platform_info}",
            "-" * 72,
        ]
        for c in self.checks:
            tag = "[PASS]" if c.passed else "[FAIL]"
            lines.append(f"{tag} {c.name:<28} {c.latency_ms:7.3f} ms  {c.detail}")
        lines.append("-" * 72)
        status = "ALL CHECKS PASSED" if self.overall_ok else "DEGRADED / CHECKS FAILED"
        lines.append(f"Status: {status} ({self.total_latency_ms:.2f} ms total)")
        return "\n".join(lines)


class ResearchDoctor:
    """Runs end-to-end diagnostic probes on the local deep research engine."""

    def run(self) -> DoctorReport:
        t_start = time.perf_counter()
        checks: List[ProbeCheck] = []

        # 1. Runtime health
        t0 = time.perf_counter()
        health = HealthMonitor().check()
        checks.append(
            ProbeCheck(
                name="runtime_health",
                passed=health.status == "healthy",
                latency_ms=(time.perf_counter() - t0) * 1000.0,
                detail=f"status={health.status}",
            )
        )

        # 2. BM25 Content Distiller
        t0 = time.perf_counter()
        sample_html = (
            "<nav>Cookie Policy Sign In</nav>"
            "<p>Majorana zero modes enable fault-tolerant topological quantum computation.</p>"
            "<p>Paraphernalia noise filler text without relevance.</p>"
        ) * 10
        distilled = ContentDistiller().distill(sample_html, query="Majorana topological quantum")
        distill_ok = distilled.distilled_char_count > 0 and distilled.compression_ratio > 0.0
        checks.append(
            ProbeCheck(
                name="bm25_content_distiller",
                passed=distill_ok,
                latency_ms=(time.perf_counter() - t0) * 1000.0,
                detail=f"compression={int(distilled.compression_ratio * 100)}%, saved={distilled.estimated_tokens_saved}tok",
            )
        )

        # 3. SHA-256 FactLedger Verification
        t0 = time.perf_counter()
        ledger = FactLedger()
        ref_id = ledger.add_snippet(
            "Braiding reduces qubit overhead from 1000:1 to 10:1.",
            "https://arxiv.org/abs/1234",
            "QEC",
        )
        snip = ledger.get_snippet(ref_id)
        ok_claim = ledger.verify_claim("Braiding reduces qubit overhead from 1000:1 to 10:1.")
        bad_claim = ledger.verify_claim("Braiding reduces qubit overhead from 500:1 to 2:1.")
        ledger_ok = bool(ok_claim.get("verified")) and (not bool(bad_claim.get("verified")))
        ev_hash = snip.sha256_hash[:12] if snip else "none"
        checks.append(
            ProbeCheck(
                name="sha256_fact_ledger",
                passed=ledger_ok,
                latency_ms=(time.perf_counter() - t0) * 1000.0,
                detail=f"evidence_hash={ev_hash}...",
            )
        )

        # 4. Offline ResearchEngine pipeline
        t0 = time.perf_counter()
        engine = ResearchEngine()
        mock_evidence = [
            {
                "title": "Majorana Zero Modes",
                "url": "https://arxiv.org/abs/2601.0001",
                "text": "Majorana zero modes store quantum information non-locally for fault-tolerant topological quantum computation.",
            }
        ]
        dossier = engine.research(
            "Topological Quantum Computing",
            depth=1,
            mock_evidence=mock_evidence,
        )
        engine_ok = dossier.sources_count > 0 and bool(dossier.root_evidence_hash)
        checks.append(
            ProbeCheck(
                name="research_engine_mock_run",
                passed=engine_ok,
                latency_ms=(time.perf_counter() - t0) * 1000.0,
                detail=f"sources={dossier.sources_count}, saved={dossier.estimated_tokens_saved}tok",
            )
        )

        overall_ok = all(c.passed for c in checks)
        total_ms = (time.perf_counter() - t_start) * 1000.0
        return DoctorReport(
            overall_ok=overall_ok,
            python_version=platform.python_version(),
            platform_info=f"{platform.system()} {platform.release()}",
            checks=checks,
            total_latency_ms=total_ms,
        )
