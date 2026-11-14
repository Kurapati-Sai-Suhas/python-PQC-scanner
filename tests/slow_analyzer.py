"""Test helper loaded inside the analysis worker process: sleeps on files named `a_slow*.py`."""
import time
from pqscan.pipeline import _analyze_file


def analyze(path: str, rel: str):
    if rel.split("/")[-1].startswith("a_slow"):
        time.sleep(30)
    return _analyze_file(path, rel)
