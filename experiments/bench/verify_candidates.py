"""Verify candidate repositories for the real-repository benchmark split and write the
frozen manifest (docs/benchmark/repository_split.md Sec. 2 and 4).

Usage:
    python experiments/bench/verify_candidates.py <clone_dir> <out_json> <out_md> [--no-network]

For each candidate: GitHub metadata (stars, licence, default branch, pushed_at) from the
public API (unauthenticated), a shallow clone at the default branch, Python-file count,
regex candidate count (same over-approximation as the pilot), pyca / PyCryptodome import
counts, test-path share, exclusion-list membership, and an accept/reject decision with a
reason. Decisions are mechanical; thresholds are stated in the output.
"""
from __future__ import annotations
import json, os, re, subprocess, sys, urllib.request, datetime
from pathlib import Path

CANDIDATES = {
    "development": ["paramiko/paramiko", "mpdavis/python-jose", "jpadilla/pyjwt", "lepture/authlib"],
    "validation": ["latchset/jwcrypto", "ronf/asyncssh", "secure-systems-lab/securesystemslib"],
    "test": ["Netflix/lemur", "googleapis/google-auth-library-python", "MatthiasValvekens/pyHanko",
             "keylime/keylime", "in-toto/in-toto", "theupdateframework/python-tuf",
             "mitmproxy/mitmproxy", "twisted/twisted",
             # second round of candidates (round 1 left only two accepted test repositories)
             "secdev/scapy", "saltstack/salt", "ansible/ansible", "aws/aws-encryption-sdk-python",
             "fortra/impacket", "openstack/barbican", "jborean93/pyspnego"],
}
# repositories used by any baseline for tuning/validation (docs/benchmark/repository_split.md Sec. 1)
EXCLUDED_FROM_TEST = {
    "certbot/certbot", "jpadilla/pyjwt", "lepture/authlib", "mpdavis/python-jose", "oauthlib/oauthlib",
    "paramiko/paramiko", "sigstore/sigstore-python", "borgbackup/borg", "astral-sh/uv",
    "tlsfuzzer/python-ecdsa", "sybrenstuvel/python-rsa", "pyca/cryptography", "pyca/pyopenssl",
    "tlsfuzzer/tlslite-ng", "open-quantum-safe/liboqs-python",
}
REGEX = re.compile(r"generate_private_key|load_pem_|load_der_|load_ssh_|RSA\.(generate|import_key|construct)|"
                   r"ECC\.(generate|import_key|construct)|\.import_key\(|\.sign\(|\.verify\(|\.exchange\(|"
                   r"\.encrypt\(|\.decrypt\(|PKCS1_OAEP|PKCS1_v1_5|pkcs1_15|\bpss\b|\bDSS\b|ECDH\(|x25519\.|X25519|"
                   r"rsa\.|ec\.|RSAPrivateKey|RSAPublicKey|EllipticCurve")
PYCA = re.compile(r"^\s*(from|import)\s+cryptography\b", re.M)
PYCRYPTODOME = re.compile(r"^\s*(from|import)\s+(Crypto|Cryptodome)\b", re.M)
MIN_STARS, MIN_CANDIDATES = 100, 10


def gh(repo: str, network: bool) -> dict:
    if not network:
        return {}
    req = urllib.request.Request(f"https://api.github.com/repos/{repo}", headers={"User-Agent": "pqscan-bench-verify"})
    with urllib.request.urlopen(req, timeout=30) as r:
        d = json.load(r)
    return {"stars": d.get("stargazers_count"), "license": (d.get("license") or {}).get("spdx_id"),
            "default_branch": d.get("default_branch"), "pushed_at": d.get("pushed_at"), "archived": d.get("archived")}


def clone(repo: str, dest: Path, network: bool) -> dict:
    if not dest.exists():
        if not network:
            return {"error": "not cloned (no network)"}
        subprocess.run(["git", "clone", "-q", "--depth", "1", f"https://github.com/{repo}.git", str(dest)], check=True)
    commit = subprocess.check_output(["git", "-C", str(dest), "rev-parse", "HEAD"], text=True).strip()
    date = subprocess.check_output(["git", "-C", str(dest), "log", "-1", "--format=%cs"], text=True).strip()
    py = [p for p in dest.rglob("*.py") if ".git" not in p.parts]
    n_cand = n_pyca = n_pcd = n_test_cand = 0
    files_with_crypto = 0
    for p in py:
        try:
            t = p.read_text(encoding="utf-8", errors="replace")
        except OSError:
            continue
        c = len(REGEX.findall(t))
        if PYCA.search(t) or PYCRYPTODOME.search(t):
            files_with_crypto += 1
            n_cand += c
            if re.search(r"(^|[\\/])(tests?|testing)([\\/]|$)|test_[^\\/]*\.py$|_test\.py$", str(p.relative_to(dest))):
                n_test_cand += c
        n_pyca += len(PYCA.findall(t)); n_pcd += len(PYCRYPTODOME.findall(t))
    lic_head = ""
    for name in ("LICENSE", "LICENSE.txt", "LICENSE.md", "LICENCE", "COPYING", "LICENSE.rst"):
        f = dest / name
        if f.exists():
            lic_head = " ".join(f.read_text(encoding="utf-8", errors="replace").split())[:160]
            break
    return {"commit": commit, "commit_date": date, "py_files": len(py), "license_file_head": lic_head, "files_importing_crypto_libs": files_with_crypto,
            "regex_candidates_in_crypto_files": n_cand, "candidates_in_test_paths": n_test_cand,
            "pyca_imports": n_pyca, "pycryptodome_imports": n_pcd}


def main() -> None:
    clone_dir, out_json, out_md = Path(sys.argv[1]), Path(sys.argv[2]), Path(sys.argv[3])
    network = "--no-network" not in sys.argv
    clone_dir.mkdir(parents=True, exist_ok=True)
    result = {"generated": datetime.datetime.now(datetime.UTC).isoformat(timespec="seconds"),
              "thresholds": {"min_stars": MIN_STARS, "min_regex_candidates": MIN_CANDIDATES}, "repositories": []}
    for split, repos in CANDIDATES.items():
        for repo in repos:
            rec = {"repo": repo, "proposed_split": split}
            try:
                rec.update(gh(repo, network))
                rec.update(clone(repo, clone_dir / repo.replace("/", "__"), network))
            except Exception as e:  # noqa: BLE001 - record and continue
                rec["error"] = f"{type(e).__name__}: {e}"
            rec["in_baseline_corpus"] = repo in EXCLUDED_FROM_TEST
            reasons = []
            if rec.get("error"): reasons.append("error")
            if rec.get("stars") is not None and rec["stars"] < MIN_STARS: reasons.append(f"stars<{MIN_STARS}")
            if rec.get("regex_candidates_in_crypto_files", 0) < MIN_CANDIDATES: reasons.append(f"candidates<{MIN_CANDIDATES}")
            if rec.get("archived"): reasons.append("archived")
            if split == "test" and rec["in_baseline_corpus"]: reasons.append("in baseline corpus")
            if rec.get("license") in (None, "NOASSERTION"):
                head = (rec.get("license_file_head") or "").lower()
                if any(k in head for k in ("mit license", "apache license", "bsd", "gnu lesser", "gnu general", "mozilla public", "eclipse public")):
                    rec["license"] = "from LICENSE file: " + rec["license_file_head"][:60]
                else:
                    reasons.append("licence unverified")
            rec["decision"] = "accept" if not reasons else "reject"
            rec["reasons"] = reasons
            result["repositories"].append(rec)
            print(f"{repo:45} {split:11} {rec['decision']:7} {reasons} cand={rec.get('regex_candidates_in_crypto_files')} pyca={rec.get('pyca_imports')} pcd={rec.get('pycryptodome_imports')}")
    out_json.write_text(json.dumps(result, indent=2), encoding="utf-8")
    lines = ["# Candidate repository verification (generated by experiments/bench/verify_candidates.py)", "",
             f"Generated {result['generated']}. Thresholds: stars >= {MIN_STARS}, regex candidates in crypto-importing files >= {MIN_CANDIDATES}, OSI licence, not archived, test split excludes baseline corpora.", "",
             "| Repo | Split | Commit | Date | Stars | Licence | .py files | crypto files | candidates | in tests | pyca imports | PyCryptodome imports | baseline corpus | Decision | Reasons |",
             "|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|"]
    for r in result["repositories"]:
        lines.append(f"| {r['repo']} | {r['proposed_split']} | {str(r.get('commit',''))[:10]} | {r.get('commit_date','')} | {r.get('stars','')} | {r.get('license','')} | {r.get('py_files','')} | {r.get('files_importing_crypto_libs','')} | {r.get('regex_candidates_in_crypto_files','')} | {r.get('candidates_in_test_paths','')} | {r.get('pyca_imports','')} | {r.get('pycryptodome_imports','')} | {'yes' if r['in_baseline_corpus'] else 'no'} | {r['decision']} | {', '.join(r['reasons'])} |")
    out_md.write_text("\n".join(lines), encoding="utf-8")


if __name__ == "__main__":
    main()
