"""PQScan demo UI: a local web page that runs the REAL pqscan CLI on a fixed set of inputs and explains its output.

    .venv\\Scripts\\python demo_ui\\server.py          then open http://127.0.0.1:8765

Safety and integrity:
* Listens on 127.0.0.1 only. Inputs are a fixed list (no arbitrary paths from the browser); the source viewer only
  reads files inside the chosen input's folder.
* Every scan is a fresh subprocess call of the installed `pqscan` CLI; nothing is cached or pre-recorded.
* Inputs: the synthetic demo fixture and the synthetic PQ/T-combination fixture (written for this project), and the
  installed pyca/cryptography and PyCryptodome sources (real third-party library code, read in place, never modified).
  The sealed benchmark repositories are never used.
* Counts shown are what pqscan reported; they are not accuracy (no labels exist for these inputs).
Standard library only (plus pqscan's own dependencies for CBOM/SARIF validation).
"""
from __future__ import annotations

import json
import os
import secrets
import subprocess
import sys
import tempfile
import time
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from importlib.metadata import version
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent
BIN = Path(sys.executable).parent
PQSCAN = BIN / ("pqscan.exe" if os.name == "nt" else "pqscan")
SEMGREP = BIN / ("semgrep.exe" if os.name == "nt" else "semgrep")
WORK = Path(tempfile.mkdtemp(prefix="pqscan_ui_"))
DOWNLOADS: dict[str, Path] = {}


def _hybrid_fixture() -> Path:
    out = WORK / "fixtures"
    subprocess.run([sys.executable, str(ROOT / "docs/audit/e2e/make_fixtures.py"), str(out)], check=True,
                   capture_output=True)
    return out / "hybrid"


def _inputs() -> dict:
    import cryptography
    import Crypto
    return {
        "demo": {"title": "Demo project (synthetic)", "kind": "synthetic",
                 "path": ROOT / "docs/demo/demo_repo",
                 "about": "7 small Python files written for this project. Each one shows one decision path: "
                          "signing, encryption, key agreement, key inventory and two deliberately ambiguous cases."},
        "hybrid": {"title": "PQ/T combination example (synthetic)", "kind": "synthetic",
                   "path": _hybrid_fixture(),
                   "about": "One file: X25519 combined with ML-KEM-768 in one hash (a detected PQ/T combination) next to a "
                            "class that computes both but never combines them (must still migrate)."},
        "cryptography": {"title": f"pyca/cryptography {version('cryptography')} (real library)", "kind": "real",
                         "path": Path(cryptography.__file__).resolve().parent,
                         "about": "The installed source of the most widely used Python crypto library. Library-internal "
                                  "code, not an application: most keys come from callers, so expect many abstentions. ~5 s."},
        "pycryptodome": {"title": f"PyCryptodome {version('pycryptodome')} (real library)", "kind": "real",
                         "path": Path(Crypto.__file__).resolve().parent,
                         "about": "The installed source of PyCryptodome (228 files). Most public-key sites are in its own "
                                  "self-tests. The full scan takes about 40-60 s."},
    }


INPUTS = _inputs()


def _run(cmd: list[str], timeout: int = 900) -> tuple[int, str, str, float]:
    env = dict(os.environ, PYTHONIOENCODING="utf-8")
    t0 = time.perf_counter()
    p = subprocess.run(cmd, capture_output=True, text=True, encoding="utf-8", errors="replace", env=env, timeout=timeout)
    return p.returncode, p.stdout, p.stderr, round(time.perf_counter() - t0, 1)


def scan(body: dict) -> dict:
    key = body.get("input")
    if key not in INPUTS:
        raise ValueError("unknown input")
    threshold = body.get("threshold", "T2")
    arm = body.get("arm", "full")
    if threshold not in ("T0", "T1", "T2", "T3") or arm not in ("full", "method+args+recv", "method+args", "method-only"):
        raise ValueError("bad option")
    out = WORK / f"scan_{secrets.token_hex(4)}.json"
    cmd = [str(PQSCAN), "scan", str(INPUTS[key]["path"]), "--format", "json", "--tier-threshold", threshold,
           "--arm", arm, "-o", str(out)]
    if body.get("exclude_tests"):
        cmd.append("--exclude-tests")
    rc, so, se, secs = _run(cmd)
    if rc != 0:
        return {"ok": False, "exit_code": rc, "stderr": se[-2000:], "seconds": secs}
    report = json.loads(out.read_text(encoding="utf-8"))
    shown = ["pqscan", "scan", f"<{key}>", "--format", "json", "--tier-threshold", threshold, "--arm", arm]
    if body.get("exclude_tests"):
        shown.append("--exclude-tests")
    return {"ok": True, "exit_code": rc, "seconds": secs, "command": " ".join(shown), "report": report}


def export(body: dict) -> dict:
    key, fmt = body.get("input"), body.get("format")
    if key not in INPUTS or fmt not in ("cbom", "sarif", "json"):
        raise ValueError("bad export request")
    ext = {"cbom": "cbom.json", "sarif": "sarif", "json": "json"}[fmt]
    out = WORK / f"{key}_{secrets.token_hex(3)}.{ext}"
    rc, so, se, secs = _run([str(PQSCAN), "scan", str(INPUTS[key]["path"]), "--format", fmt, "-o", str(out)])
    if rc != 0:
        return {"ok": False, "exit_code": rc, "stderr": se[-2000:]}
    text = out.read_text(encoding="utf-8")
    if fmt == "cbom":
        from cyclonedx.schema import SchemaVersion
        from cyclonedx.validation.json import JsonStrictValidator
        err = JsonStrictValidator(SchemaVersion.V1_6).validate_str(text)
        check = "VALID against CycloneDX 1.6 (strict)" if err is None else f"INVALID: {str(err)[:200]}"
        count = f"{len(json.loads(text).get('components', []))} components"
    elif fmt == "sarif":
        import jsonschema
        schema = json.loads((ROOT / "pqscan/export/schemas/sarif-2.1.0.json").read_text(encoding="utf-8"))
        errs = list(jsonschema.Draft4Validator(schema).iter_errors(json.loads(text)))
        check = "VALID against SARIF 2.1.0" if not errs else f"INVALID: {errs[0].message[:200]}"
        count = f"{sum(len(r.get('results', [])) for r in json.loads(text).get('runs', []))} results"
    else:
        check, count = "written", f"{len(json.loads(text).get('findings', []))} findings"
    token = secrets.token_hex(8)
    DOWNLOADS[token] = out
    return {"ok": True, "exit_code": rc, "seconds": secs, "check": check, "count": count, "bytes": len(text.encode()),
            "download": f"/api/download/{token}", "name": out.name, "preview": text[:2500]}


def source(key: str, rel: str, line: int, end: int) -> dict:
    if key not in INPUTS:
        raise ValueError("unknown input")
    root = INPUTS[key]["path"].resolve()
    p = (root / rel).resolve()
    if root not in p.parents or not p.is_file():
        raise ValueError("file outside the input")
    lines = p.read_text(encoding="utf-8", errors="replace").splitlines()
    a, b = max(1, line - 6), min(len(lines), max(end, line) + 6)
    return {"file": rel, "start": a, "lines": lines[a - 1:b], "hit": [line, max(end, line)]}


def environment() -> dict:
    def ver(exe):
        try:
            return subprocess.run([str(exe), "--version"], capture_output=True, text=True, timeout=60).stdout.strip()
        except Exception as e:  # noqa: BLE001
            return f"unavailable ({e.__class__.__name__})"
    commit = "unknown"
    try:
        commit = subprocess.run(["git", "rev-parse", "--short", "HEAD"], cwd=ROOT, capture_output=True, text=True).stdout.strip()
    except Exception:  # noqa: BLE001
        pass
    return {"pqscan": ver(PQSCAN), "semgrep": ver(SEMGREP), "python": sys.version.split()[0], "commit": commit,
            "inputs": [{"key": k, "title": v["title"], "kind": v["kind"], "about": v["about"],
                        "path": str(v["path"]).replace(str(Path.home()), "~")} for k, v in INPUTS.items()]}


class Handler(BaseHTTPRequestHandler):
    def log_message(self, fmt, *args):
        sys.stderr.write("  " + (fmt % args) + "\n")

    def _send(self, code: int, body: bytes, ctype: str, extra: dict | None = None):
        self.send_response(code)
        self.send_header("Content-Type", ctype)
        self.send_header("Content-Length", str(len(body)))
        self.send_header("Cache-Control", "no-store")
        for k, v in (extra or {}).items():
            self.send_header(k, v)
        self.end_headers()
        self.wfile.write(body)

    def _json(self, obj, code=200):
        self._send(code, json.dumps(obj).encode("utf-8"), "application/json; charset=utf-8")

    def do_GET(self):  # noqa: N802
        try:
            if self.path in ("/", "/index.html"):
                return self._send(200, (HERE / "index.html").read_bytes(), "text/html; charset=utf-8")
            if self.path == "/api/env":
                return self._json(environment())
            if self.path.startswith("/api/source?"):
                from urllib.parse import parse_qs, urlparse
                q = parse_qs(urlparse(self.path).query)
                return self._json(source(q["input"][0], q["file"][0], int(q["line"][0]), int(q.get("end", q["line"])[0])))
            if self.path.startswith("/api/download/"):
                p = DOWNLOADS.get(self.path.rsplit("/", 1)[-1])
                if not p:
                    return self._json({"error": "unknown download"}, 404)
                return self._send(200, p.read_bytes(), "application/octet-stream",
                                  {"Content-Disposition": f'attachment; filename="{p.name}"'})
            return self._json({"error": "not found"}, 404)
        except Exception as e:  # noqa: BLE001
            return self._json({"error": str(e)}, 400)

    def do_POST(self):  # noqa: N802
        try:
            body = json.loads(self.rfile.read(int(self.headers.get("Content-Length", "0") or 0)) or b"{}")
            if self.path == "/api/scan":
                return self._json(scan(body))
            if self.path == "/api/export":
                return self._json(export(body))
            return self._json({"error": "not found"}, 404)
        except Exception as e:  # noqa: BLE001
            return self._json({"error": str(e)}, 400)


def main() -> None:
    port = int(os.environ.get("PQSCAN_UI_PORT", "8765"))
    for exe in (PQSCAN, SEMGREP):
        if not exe.exists():
            sys.exit(f"not found: {exe}  (run this with the project's .venv Python)")
    srv = ThreadingHTTPServer(("127.0.0.1", port), Handler)
    print(f"PQScan demo UI running at http://127.0.0.1:{port}   (Ctrl+C to stop)")
    print(f"pqscan: {PQSCAN}")
    try:
        srv.serve_forever()
    except KeyboardInterrupt:
        print("stopped")


if __name__ == "__main__":
    main()
