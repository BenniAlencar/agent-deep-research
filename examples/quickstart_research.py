"""Minimal quickstart example for agent-deep-research (offline mock mode)."""

import pathlib
import sys

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[1] / "src"))

from agent_deep_research import ResearchEngine


def main() -> None:
    engine = ResearchEngine()
    mock_evidence = [
        {
            "title": "Topological Qubits Overview",
            "url": "https://arxiv.org/abs/2601.0001",
            "text": (
                "Majorana zero modes enable fault-tolerant topological quantum computation "
                "by storing quantum information non-locally and reducing physical-to-logical qubit overhead."
            ),
        }
    ]
    dossier = engine.research(
        "Topological Quantum Error Correction",
        depth=1,
        mock_evidence=mock_evidence,
    )
    print("Topic:", dossier.topic)
    print("Sources:", dossier.sources_count)
    print("Root Evidence Hash:", dossier.root_evidence_hash)
    print(f"Compression: {int(dossier.compression_ratio * 100)}% ({dossier.estimated_tokens_saved} tokens saved)")


if __name__ == "__main__":
    main()
