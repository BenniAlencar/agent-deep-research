import sys
from pathlib import Path

# Add src to sys.path so tests can import agent_deep_research without requiring env var
src_path = Path(__file__).parent.parent / "src"
if str(src_path) not in sys.path:
    sys.path.insert(0, str(src_path))
