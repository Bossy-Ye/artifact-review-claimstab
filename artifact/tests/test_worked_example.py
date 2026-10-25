"""EX-C7 worked example (paper Figs. 4-5) recomputed from its per-cell trace."""
import importlib.util
import sys
from pathlib import Path

SCRIPT = Path(__file__).resolve().parents[1] / "scripts" / "worked_example_exc7.py"


def test_exc7_worked_example_matches_paper() -> None:
    spec = importlib.util.spec_from_file_location("worked_example_exc7", SCRIPT)
    mod = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = mod
    spec.loader.exec_module(mod)
    assert mod.main() == 0
