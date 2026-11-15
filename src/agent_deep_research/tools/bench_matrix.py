"""
Multi-workload token compression and distillation benchmark matrix for agent-deep-research.
"""

from __future__ import annotations

import time
from dataclasses import dataclass
from typing import Any, Dict, List, Optional

from ..core.distiller import ContentDistiller


@dataclass
class MatrixRow:
    workload: str
    raw_chars: int
    distilled_chars: int
    compression_pct: float
    tokens_saved: int
    latency_ms: float

    def to_dict(self) -> Dict[str, Any]:
        return {
            "workload": self.workload,
            "raw_chars": self.raw_chars,
            "distilled_chars": self.distilled_chars,
            "compression_pct": round(self.compression_pct, 2),
            "tokens_saved": self.tokens_saved,
            "latency_ms": round(self.latency_ms, 3),
        }


DEFAULT_WORKLOADS: Dict[str, tuple[str, str]] = {
    "quantum_html": (
        "topological qubits majorana braiding overhead",
        (
            "<nav>Home | Pricing | Cookie Policy | Sign In</nav>"
            "<p>Topological quantum computation stores quantum information non-locally in Majorana zero modes.</p>"
            "<p>Braiding operations reduce physical-to-logical qubit overhead from 1000:1 to 10:1.</p>"
            "<footer>Copyright 2026 TechCorp. Subscribe to our newsletter.</footer>"
        ) * 25,
    ),
    "llm_inference_html": (
        "kv cache quantization int4 vram consumer gpu",
        (
            "<aside>Advertisement: Buy cloud GPUs now!</aside>"
            "<p>Quantized KV caches using q4_0 reduce per-token VRAM footprint by 71.9% on 8GB consumer GPUs.</p>"
            "<p>Attention and hot MoE experts remain pinned in VRAM while cold experts stream from host RAM.</p>"
            "<div>Related links: Terms of service, privacy notice, cookie banner.</div>"
        ) * 25,
    ),
    "ast_security_html": (
        "ast static analysis sandbox python reflection",
        (
            "<header>Navigation Menu | Login | Register</header>"
            "<p>Pre-execution AST scanning blocks os, subprocess, and reflective __subclasses__ escapes in under 0.2ms.</p>"
            "<p>Ephemeral workspaces compute SHA-256 diffs without Docker cold-start overhead.</p>"
            "<footer>All rights reserved. Follow us on social media.</footer>"
        ) * 25,
    ),
}


class BenchmarkMatrix:
    """Runs reproducible BM25 distillation benchmarks across multiple document sizes and topics."""

    def __init__(self, max_chunks: int = 5) -> None:
        self.distiller = ContentDistiller()
        self.max_chunks = max_chunks

    def run(
        self,
        workloads: Optional[Dict[str, tuple[str, str]]] = None,
        reps: int = 3,
    ) -> List[MatrixRow]:
        suite = workloads or DEFAULT_WORKLOADS
        reps = max(1, int(reps))
        rows: List[MatrixRow] = []

        for name, (query, html) in suite.items():
            total_ms = 0.0
            last = None
            for _ in range(reps):
                t0 = time.perf_counter()
                last = self.distiller.distill(html, query=query, title=name, max_chunks=self.max_chunks)
                total_ms += (time.perf_counter() - t0) * 1000.0

            assert last is not None
            rows.append(
                MatrixRow(
                    workload=name,
                    raw_chars=last.original_char_count,
                    distilled_chars=last.distilled_char_count,
                    compression_pct=last.compression_ratio * 100.0,
                    tokens_saved=last.estimated_tokens_saved,
                    latency_ms=total_ms / reps,
                )
            )
        return rows

    @staticmethod
    def format_table(rows: List[MatrixRow]) -> str:
        header = (
            f"{'Workload':<20} | {'Raw Chars':>10} | {'Distilled':>10} | "
            f"{'Savings':>8} | {'Tokens Saved':>12} | {'Latency':>9}"
        )
        sep = "-" * len(header)
        lines = [header, sep]
        for r in rows:
            lines.append(
                f"{r.workload:<20} | {r.raw_chars:10,d} | {r.distilled_chars:10,d} | "
                f"{r.compression_pct:7.1f}% | {r.tokens_saved:12,d} | {r.latency_ms:6.2f} ms"
            )
        return "\n".join(lines)
