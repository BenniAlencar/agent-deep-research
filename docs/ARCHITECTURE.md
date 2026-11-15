# Architecture — `agent-deep-research`

`agent-deep-research` follows the **Benni Master OS v9.4** modular three-tier package layout:

1. **`core/` (Search, Distillation & Provenance)**
   - `search.py`: Zero-key `MultiSearchAdapter` supporting DuckDuckGo, Wikipedia, ArXiv, and deterministic offline `mock_mode`.
   - `distiller.py`: HTML noise-stripper (`clean_html`) and vectorized BM25 passage ranker (`ContentDistiller`, `BM25Distiller`) achieving >85% token compression.
   - `verifier.py`: Cryptographic `FactLedger` assigning `sha256(source_url + text)` hashes and blocking numerical contradictions.
   - `engine.py`: `ResearchEngine` orchestrating multi-hop plans into structured `ResearchDossier` reports.

2. **`serve/` (Runtime Interfaces & Observability)**
   - `mcp_bridge.py`: Native JSON-RPC 2.0 stdio Model Context Protocol server (`deep_research`, `quick_search`, `verify_claim`).
   - `telemetry.py`: Thread-safe rolling P50/P90/P99 latency, source count, and token-savings collector.
   - `health_monitor.py`: Runtime health probe verifying distiller, FactLedger, and mock search readiness.
   - `__main__.py`: Unified CLI entrypoint (`run`, `search`, `mcp`, `benchmark`, `doctor`, `matrix`, `health`).

3. **`tools/` (Diagnostics & Benchmarks)**
   - `doctor.py`: End-to-end diagnostic probe (`ResearchDoctor`) with structured JSON and human-readable reports.
   - `bench_matrix.py`: Multi-workload BM25 compression & latency matrix (`BenchmarkMatrix`).
