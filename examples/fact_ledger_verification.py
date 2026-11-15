"""Demonstrates SHA-256 FactLedger citation verification and ResearchTelemetry."""

import pathlib
import sys

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[1] / "src"))

from agent_deep_research import FactLedger, ResearchTelemetry


def main() -> None:
    ledger = FactLedger()
    ref_id = ledger.add_snippet(
        "Quantized KV caches using q4_0 reduce VRAM usage by 71.9% on 8GB GPUs.",
        "https://github.com/Benni-OS/benni-inference-engine",
        "BIE Spec",
    )
    snip = ledger.get_snippet(ref_id)
    print("Snippet Hash:", snip.sha256_hash[:16] if snip else "none")

    ok = ledger.verify_claim("Quantized KV caches using q4_0 reduce VRAM usage by 71.9%")
    contradiction = ledger.verify_claim("Quantized KV caches using q4_0 reduce VRAM usage by 12.0%")
    print("Verified claim:", ok["verified"])
    print("Contradiction blocked:", not contradiction["verified"])

    telemetry = ResearchTelemetry()
    telemetry.record("verify", latency_ms=1.4, sources_count=1, tokens_saved=450, compression_ratio=0.85)
    print("Telemetry:", telemetry.snapshot())


if __name__ == "__main__":
    main()
