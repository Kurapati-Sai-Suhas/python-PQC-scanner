"""Drive Quantum-Safe Auditor's regex stage only (no LLM enrichment)."""
import sys, json, os
sys.path.insert(0, sys.argv[1])          # repo root of quantum-safe-auditor
from scanner.crypto_scanner import CryptoScanner, VULNERABLE_PATTERNS
from local_scan.local_repo_scanner import LocalRepoScanner
target = sys.argv[2]
files = LocalRepoScanner(repo_path=target, exclude_paths=[], max_files=5000).get_files()
sc = CryptoScanner(client=None, enricher=None)
out = []
for f in files:
    for c in sc._regex_sweep(f["path"], f["content"].splitlines()):
        c["file"] = f["path"]; out.append(c)
json.dump({"n_files": len(files), "findings": out}, open(sys.argv[3], "w"), indent=1)
print(len(files), "files,", len(out), "regex findings")
