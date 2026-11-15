"""Multi-workload BM25 distillation benchmark script for agent-deep-research."""

import pathlib
import sys

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[1] / "src"))

from agent_deep_research.tools import BenchmarkMatrix


def main() -> None:
    matrix = BenchmarkMatrix()
    rows = matrix.run(reps=3)
    print(matrix.format_table(rows))


if __name__ == "__main__":
    main()
