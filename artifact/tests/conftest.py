"""Put the bundled minimal package (artifact/src) first on sys.path so these tests
exercise the bundled CLAIMSTAB-QC verdict-core, not any separately installed copy.
No qiskit/pandas needed for the verdict-core tests."""
import sys
from pathlib import Path

SRC = Path(__file__).resolve().parents[1] / "src"
sys.path.insert(0, str(SRC))
