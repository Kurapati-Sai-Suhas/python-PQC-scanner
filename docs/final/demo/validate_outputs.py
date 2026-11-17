"""Independent validation of the final demonstration outputs (docs/final/demo/outputs/real).

Checks every CBOM with cyclonedx-python-lib's strict CycloneDX 1.6 validator. Checks every SARIF file with
jsonschema against the OASIS SARIF 2.1.0 schema bundled in pqscan/export/schemas. Both checks run outside
pqscan's export path, which validates the CBOM itself before writing it. `.gz` files are read decompressed.

    .venv/Scripts/python docs/final/demo/validate_outputs.py
"""
from __future__ import annotations

import gzip
import json
import sys
from pathlib import Path

import jsonschema
from cyclonedx.schema import SchemaVersion
from cyclonedx.validation.json import JsonStrictValidator

ROOT = Path(__file__).resolve().parents[3]
OUT = Path(__file__).resolve().parent / "outputs" / "real"
SARIF_SCHEMA = json.loads((ROOT / "pqscan" / "export" / "schemas" / "sarif-2.1.0.json").read_text(encoding="utf-8"))


def _read(p: Path) -> str:
    return gzip.decompress(p.read_bytes()).decode("utf-8") if p.suffix == ".gz" else p.read_text(encoding="utf-8")


def main() -> int:
    bad = 0
    fixture = ROOT / "docs" / "demo" / "outputs"     # lecturer-demo fixture outputs (synthetic), checked too
    cboms = [fixture / "03_cbom.json", *sorted(OUT.glob("*_cbom.json*"))]
    sarifs = [fixture / "04_scan.sarif", *sorted(OUT.glob("*.sarif*"))]
    for p in cboms:
        text = _read(p)
        err = JsonStrictValidator(SchemaVersion.V1_6).validate_str(text)
        comps = json.loads(text).get("components", [])
        print(f"CBOM  {p.relative_to(ROOT).as_posix()}: {'VALID' if err is None else 'INVALID: ' + str(err)[:200]} "
              f"(CycloneDX 1.6 strict; {len(comps)} components)")
        bad += err is not None
    for p in sarifs:
        doc = json.loads(_read(p))
        errors = list(jsonschema.Draft4Validator(SARIF_SCHEMA).iter_errors(doc))
        results = sum(len(r.get("results", [])) for r in doc.get("runs", []))
        print(f"SARIF {p.relative_to(ROOT).as_posix()}: {'VALID' if not errors else 'INVALID: ' + errors[0].message[:200]} "
              f"(SARIF 2.1.0 schema; {results} results)")
        bad += bool(errors)
    return 1 if bad else 0


if __name__ == "__main__":
    sys.exit(main())
