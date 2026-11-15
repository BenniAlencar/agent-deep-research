"""Provenance & runtime health gate runner for agent-deep-research."""

import pathlib
import sys

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[1] / "src"))

from agent_deep_research.tools import ResearchDoctor


def main() -> None:
    report = ResearchDoctor().run()
    print(report.format_report())
    if not report.overall_ok:
        sys.exit(1)


if __name__ == "__main__":
    main()
