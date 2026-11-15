"""
Rolling telemetry collector for agent-deep-research.
Tracks research run latencies (P50/P90/P99), sources ingested, token compression, and claim verifications.
"""

from __future__ import annotations

import threading
import time
from collections import deque
from dataclasses import dataclass
from typing import Any, Deque, Dict, List


def _percentile(sorted_vals: List[float], pct: float) -> float:
    if not sorted_vals:
        return 0.0
    if len(sorted_vals) == 1:
        return sorted_vals[0]
    idx = (len(sorted_vals) - 1) * (pct / 100.0)
    lo = int(idx)
    hi = min(lo + 1, len(sorted_vals) - 1)
    frac = idx - lo
    return sorted_vals[lo] * (1.0 - frac) + sorted_vals[hi] * frac


@dataclass
class ResearchEvent:
    timestamp: float
    kind: str  # "research" | "distill" | "verify"
    latency_ms: float
    sources_count: int
    tokens_saved: int
    compression_ratio: float


class ResearchTelemetry:
    """Thread-safe rolling window telemetry for deep research pipelines."""

    def __init__(self, max_events: int = 500) -> None:
        self._events: Deque[ResearchEvent] = deque(maxlen=max_events)
        self._lock = threading.Lock()
        self._total_runs = 0
        self._total_sources = 0
        self._total_tokens_saved = 0

    def record(
        self,
        kind: str,
        latency_ms: float,
        sources_count: int = 0,
        tokens_saved: int = 0,
        compression_ratio: float = 0.0,
    ) -> None:
        ev = ResearchEvent(
            timestamp=time.time(),
            kind=kind,
            latency_ms=max(0.0, float(latency_ms)),
            sources_count=max(0, int(sources_count)),
            tokens_saved=max(0, int(tokens_saved)),
            compression_ratio=max(0.0, min(1.0, float(compression_ratio))),
        )
        with self._lock:
            self._events.append(ev)
            self._total_runs += 1
            self._total_sources += ev.sources_count
            self._total_tokens_saved += ev.tokens_saved

    def snapshot(self) -> Dict[str, Any]:
        with self._lock:
            latencies = sorted(e.latency_ms for e in self._events)
            ratios = [e.compression_ratio for e in self._events]
            runs = self._total_runs
            sources = self._total_sources
            tokens_saved = self._total_tokens_saved
            window_count = len(self._events)

        avg_comp = (sum(ratios) / len(ratios)) if ratios else 0.0
        return {
            "total_runs": runs,
            "window_events": window_count,
            "total_sources_ingested": sources,
            "tokens_saved_total": tokens_saved,
            "avg_compression_ratio": round(avg_comp, 4),
            "latency_ms": {
                "p50": round(_percentile(latencies, 50.0), 3),
                "p90": round(_percentile(latencies, 90.0), 3),
                "p99": round(_percentile(latencies, 99.0), 3),
                "mean": round(sum(latencies) / len(latencies), 3) if latencies else 0.0,
            },
        }

    def reset(self) -> None:
        with self._lock:
            self._events.clear()
            self._total_runs = 0
            self._total_sources = 0
            self._total_tokens_saved = 0
