"""Unit tests for agent_deep_research.serve and agent_deep_research.tools."""

from agent_deep_research import (
    BenchmarkMatrix,
    HealthMonitor,
    ResearchDoctor,
    ResearchTelemetry,
)


def test_research_telemetry_percentiles_and_reset():
    tel = ResearchTelemetry(max_events=50)
    tel.record("research", 12.0, sources_count=3, tokens_saved=1200, compression_ratio=0.88)
    tel.record("distill", 4.0, sources_count=1, tokens_saved=300, compression_ratio=0.80)
    tel.record("verify", 8.0, sources_count=2, tokens_saved=500, compression_ratio=0.84)

    snap = tel.snapshot()
    assert snap["total_runs"] == 3
    assert snap["total_sources_ingested"] == 6
    assert snap["tokens_saved_total"] == 2000
    assert snap["latency_ms"]["p50"] == 8.0
    assert snap["avg_compression_ratio"] > 0.8

    tel.reset()
    assert tel.snapshot()["total_runs"] == 0


def test_health_monitor_reports_healthy():
    snap = HealthMonitor().check()
    data = snap.to_dict()
    assert snap.status == "healthy"
    assert data["distiller_ok"] is True
    assert data["ledger_ok"] is True
    assert data["search_mock_ok"] is True


def test_research_doctor_all_checks_pass():
    report = ResearchDoctor().run()
    assert report.overall_ok is True
    assert len(report.checks) == 4
    assert "ALL CHECKS PASSED" in report.format_report()
    assert report.to_dict()["overall_ok"] is True


def test_benchmark_matrix_runs_workloads():
    matrix = BenchmarkMatrix(max_chunks=3)
    rows = matrix.run(reps=1)
    assert len(rows) == 3
    assert all(r.compression_pct > 0 for r in rows)
    table = matrix.format_table(rows)
    assert "quantum_html" in table
