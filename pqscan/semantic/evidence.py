"""Evidence assembly: discover sites in one module (independently of Semgrep, so the two can be
joined and compared), type receivers, resolve arguments, trace consumers, detect hybrid context.
Output: SiteEvidence records consumed by Module C."""
from __future__ import annotations
import ast
from dataclasses import dataclass, field
from typing import Any
from .apis import (KEY_FACTORIES, CERT_LOADERS, NUMBERS_CLASSES, SIGNER_MODULES, CIPHER_MODULES, OPERATION_METHODS,
                   PQC_PREFIXES, NON_PK_OBJECTS)
from .args import ArgEvidence, resolve_args
from .consumers import ConsumerEvidence, ConsumerTracer
from .model import AbstractType, KeyType, CertType, SignerObject, CipherObject, Multi, Unknown, describe
from .typer import ModuleTyper, FunctionCtx, dotted
from .hybrid import combined_hybrid
from ..models import Candidate, CandidateKind, Library, Location, Provenance

SUPPORTED_IMPORT_ROOTS = ("cryptography", "Crypto", "Cryptodome")


@dataclass
class ReceiverInfo:
    description: str = "none"
    library: str | None = None
    algorithm: str | None = None           # None = unresolved
    private: bool | None = None
    provenance: Provenance | None = None   # single primary provenance when unique
    provenances: list[Provenance] = field(default_factory=list)
    proximate: Provenance | None = None
    curve: str | None = None
    key_size: int | None = None
    multi: bool = False
    unresolved_reason: str | None = None
    origins: list[tuple[int, str]] = field(default_factory=list)
    via_call: str | None = None


def _flatten(t: AbstractType) -> list[AbstractType]:
    return list(t.options) if isinstance(t, Multi) else [t]


def receiver_info(t: AbstractType | None) -> ReceiverInfo:
    r = ReceiverInfo(description=describe(t))
    if t is None:
        r.unresolved_reason = "no receiver"
        return r
    r.proximate = t.proximate
    r.via_call = t.via_call
    opts = _flatten(t)
    keys = [o.key if isinstance(o, (SignerObject, CipherObject)) else o for o in opts]
    keys = [k for kk in keys for k in (_flatten(kk) if kk is not None else [])]
    kts = [k for k in keys if isinstance(k, KeyType)]
    certs = [k for k in keys if isinstance(k, CertType)]
    if not kts and not certs:
        u = next((k for k in keys if isinstance(k, Unknown)), None)
        r.unresolved_reason = u.reason if u else "unresolved"
        return r
    r.multi = len(opts) > 1 or len(kts) > 1
    algs = {k.algorithm for k in kts} - {"ANY"}
    if len(algs) > 1 and algs <= {"Ed25519", "Ed448"}:
        algs = {"EdDSA"}          # both signature-only: one family, not a conflict
    elif len(algs) > 1 and algs <= {"X25519", "X448"}:
        algs = {"XDH"}            # both key-agreement-only
    r.algorithm = algs.pop() if len(algs) == 1 else ("ANY" if not algs else None)
    if r.algorithm is None and len(algs) > 1:
        r.unresolved_reason = "conflicting algorithms: " + "/".join(sorted(algs))
    privs = {k.private for k in kts}
    r.private = privs.pop() if len(privs) == 1 else None
    libs = {k.library for k in kts}
    r.library = libs.pop() if len(libs) == 1 else None
    provs: list[Provenance] = []
    for k in kts:
        p = k.provenance
        if k.proximate == Provenance.PARAMETER and p == Provenance.PARAMETER:
            p = Provenance.PARAMETER
        if p not in provs:
            provs.append(p)
    for c in certs:
        if Provenance.LOADED_CERTIFICATE not in provs:
            provs.append(Provenance.LOADED_CERTIFICATE)
    # an Unknown(parameter) option among real types means one path is an untyped parameter
    if any(isinstance(k, Unknown) and k.proximate == Provenance.PARAMETER for k in keys) or any(
            isinstance(k, Unknown) and k.reason in ("untyped parameter", "attribute from untyped parameter") for k in keys):
        if Provenance.PARAMETER not in provs:
            provs.append(Provenance.PARAMETER)
    r.provenances = provs
    r.provenance = provs[0] if len(provs) == 1 else None
    curves = {k.curve for k in kts if k.curve}
    r.curve = curves.pop() if len(curves) == 1 else None
    sizes = {k.key_size for k in kts if k.key_size}
    r.key_size = sizes.pop() if len(sizes) == 1 else None
    for k in kts + certs:
        for o in k.origins:
            if (o.line, o.text) not in r.origins:
                r.origins.append((o.line, o.text))
    return r


@dataclass
class SiteEvidence:
    candidate: Candidate
    site_kind: str                      # operation | key-material | signer-object | cipher-object | pqc | not-public-key
    operation: str | None = None        # sign | verify | exchange | encrypt | decrypt
    receiver: ReceiverInfo = field(default_factory=ReceiverInfo)
    args: ArgEvidence = field(default_factory=ArgEvidence)
    consumers: ConsumerEvidence = field(default_factory=ConsumerEvidence)
    hybrid_context: bool = False
    hybrid_apis: list[str] = field(default_factory=list)   # PQ APIs called in the same class/function
    origin_families: list[str] = field(default_factory=list)  # consumer families of the key-material site(s) the receiver came from
    origin_conflict: bool = False                            # those key-material sites have consumer conflicts
    hybrid_combined: bool = False                            # classical result combined with an approved PQ result (hybrid.py)
    function: str | None = None
    cls: str | None = None
    conflicts: list[str] = field(default_factory=list)
    notes: list[str] = field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        return {
            "location": vars(self.candidate.location), "api": self.candidate.api, "rule_id": self.candidate.rule_id,
            "kind": self.site_kind, "operation": self.operation,
            "receiver": {k: (v.value if isinstance(v, Provenance) else [p.value for p in v] if k == "provenances" else v)
                         for k, v in vars(self.receiver).items()},
            "args": vars(self.args), "consumers": {"families": sorted(self.consumers.families), "locations": self.consumers.locations,
                                                   "paths": self.consumers.paths, "escapes": self.consumers.escapes,
                                                   "escape_notes": self.consumers.escape_notes,
                                                   "unresolved_callees": self.consumers.unresolved_callees,
                                                   "conflicts": self.consumers.conflicts, "filtered": self.consumers.filtered},
            "hybrid_context": self.hybrid_context, "hybrid_apis": self.hybrid_apis,
            "origin_families": self.origin_families, "origin_conflict": self.origin_conflict,
            "hybrid_combined": self.hybrid_combined, "function": self.function, "class": self.cls,
            "conflicts": self.conflicts, "notes": self.notes,
        }


def _imports_supported(tree: ast.Module) -> bool:
    for node in ast.walk(tree):
        if isinstance(node, ast.Import) and any(a.name.split(".")[0] in SUPPORTED_IMPORT_ROOTS for a in node.names):
            return True
        if isinstance(node, ast.ImportFrom) and node.module and node.module.split(".")[0] in SUPPORTED_IMPORT_ROOTS:
            return True
    return False


def _loc(rel: str, node: ast.AST) -> Location:
    return Location(rel, node.lineno, node.col_offset + 1, node.end_lineno or node.lineno, (node.end_col_offset or node.col_offset) + 1)


def _pqc_calls(typer: ModuleTyper) -> list[tuple[int, str]]:
    out = []
    for node in ast.walk(typer.tree):
        if isinstance(node, ast.Call):
            fn = typer.function_at(node.lineno)
            q = typer.qualified(node.func, fn)
            if q and q.startswith(PQC_PREFIXES):
                out.append((node.lineno, q))
    return out


def analyze_source(rel_path: str, source: str) -> list[SiteEvidence]:
    """Analyse one module's source text. Never executes the code."""
    try:
        tree = ast.parse(source)
    except SyntaxError as e:
        c = Candidate(Location(rel_path, getattr(e, "lineno", 1) or 1, 1, 1, 1), "pqscan.parse-error", Library.UNKNOWN,
                      CandidateKind.METHOD_CANDIDATE, "ANY", "", "-")
        ev = SiteEvidence(candidate=c, site_kind="parse-error", notes=[f"SyntaxError: {e.msg}"])
        return [ev]
    if not _imports_supported(tree):
        return []
    typer = ModuleTyper(tree, source.splitlines())
    tracer = ConsumerTracer(typer)
    pqc_calls = _pqc_calls(typer)
    pqc_lines = {l for l, _ in pqc_calls}
    out: list[SiteEvidence] = []
    seen: set[tuple[int, int, int | None, int | None]] = set()

    def hybrid_for(fn: FunctionCtx | None, line: int) -> bool:
        cls = fn.cls if fn else typer.class_of_line(line)
        if cls is not None:
            return any(cls.lineno <= l <= (cls.end_lineno or cls.lineno) for l in pqc_lines)
        if fn is not None:
            return any(fn.node.lineno <= l <= (fn.node.end_lineno or fn.node.lineno) for l in pqc_lines)
        return False

    for node in ast.walk(tree):
        if not isinstance(node, ast.Call):
            continue
        key = (node.lineno, node.col_offset, node.end_lineno, node.end_col_offset)
        if key in seen:
            continue
        fn = typer.function_at(node.lineno)
        q = typer.qualified(node.func, fn)
        snippet = ""   # source text is never carried in evidence (secrets may sit in literals)
        # ---- key material: factories, cert loaders, numbers->key
        if q in KEY_FACTORIES or q in CERT_LOADERS:
            f = KEY_FACTORIES.get(q)
            kind = CandidateKind.LOADER if (q in CERT_LOADERS or (f and f.provenance in (Provenance.LOADED_PEM, Provenance.LOADED_DER, Provenance.LOADED_SSH))) else (
                CandidateKind.CONSTRUCT if (f and f.provenance == Provenance.CONSTRUCTED) else CandidateKind.KEYGEN)
            lib = Library.PYCRYPTODOME if (f and f.library == "pycryptodome") else Library.PYCA
            cand = Candidate(_loc(rel_path, node), f"semantic.{kind.value}", lib, kind, f.algorithm if f else "ANY", q, f.row if f else "C21", snippet)
            t = typer.type_of_expr(node, fn)
            ev = SiteEvidence(cand, "key-material", receiver=receiver_info(t), function=fn.qualname if fn else None,
                              cls=fn.cls.name if fn and fn.cls else None, hybrid_context=hybrid_for(fn, node.lineno))
            ev.consumers = tracer.trace(node, fn)
            if q in CERT_LOADERS:
                ev.receiver.provenance = Provenance.LOADED_CERTIFICATE; ev.receiver.provenances = [Provenance.LOADED_CERTIFICATE]
                ev.receiver.private = False; ev.receiver.algorithm = "ANY"; ev.receiver.library = "pyca"
            out.append(ev); seen.add(key)
            continue
        if isinstance(node.func, ast.Attribute) and node.func.attr in ("private_key", "public_key") and isinstance(node.func.value, ast.Call):
            bq = typer.qualified(node.func.value.func, fn)
            if bq in NUMBERS_CLASSES:
                t = typer.type_of_expr(node, fn)
                f = KEY_FACTORIES.get(f"{bq}.{node.func.attr}")
                cand = Candidate(_loc(rel_path, node), "semantic.construct", Library.PYCA, CandidateKind.CONSTRUCT, f.algorithm if f else "ANY",
                                 f"{bq}.{node.func.attr}", f.row if f else "C2", snippet)
                ev = SiteEvidence(cand, "key-material", receiver=receiver_info(t), function=fn.qualname if fn else None,
                                  cls=fn.cls.name if fn and fn.cls else None, hybrid_context=hybrid_for(fn, node.lineno))
                ev.consumers = tracer.trace(node, fn)
                out.append(ev); seen.add(key); seen.add((node.func.value.lineno, node.func.value.col_offset, node.func.value.end_lineno, node.func.value.end_col_offset))
                continue
        # two-step construction: `nums = RSAPrivateNumbers(...)` ... `nums.private_key()`
        if isinstance(node.func, ast.Attribute) and node.func.attr in ("private_key", "public_key") and isinstance(node.func.value, (ast.Name, ast.Attribute)):
            base_t = typer.type_of_expr(node.func.value, fn)
            if isinstance(base_t, Unknown) and base_t.reason == "numbers object":
                t = typer.type_of_expr(node, fn)
                if isinstance(t, KeyType):
                    cand = Candidate(_loc(rel_path, node), "semantic.construct", Library.PYCA, CandidateKind.CONSTRUCT, t.algorithm,
                                     f"{base_t.origins[0].text if base_t.origins else 'Numbers'}.{node.func.attr}", "C2/C9", snippet)
                    ev = SiteEvidence(cand, "key-material", receiver=receiver_info(t), function=fn.qualname if fn else None,
                                      cls=fn.cls.name if fn and fn.cls else None, hybrid_context=hybrid_for(fn, node.lineno))
                    ev.consumers = tracer.trace(node, fn)
                    out.append(ev); seen.add(key)
                    continue
        # ---- PyCryptodome signer / cipher objects (key consumers, and operations when chained)
        if q and q.startswith(("Crypto.", "Cryptodome.")) and (any(q.endswith(m + ".new") for m in SIGNER_MODULES) or any(q.endswith(m + ".new") for m in CIPHER_MODULES)):
            t = typer.type_of_expr(node, fn)
            is_signer = isinstance(t, SignerObject)
            kind = CandidateKind.SIGNER_OBJECT if is_signer else CandidateKind.CIPHER_OBJECT
            cand = Candidate(_loc(rel_path, node), f"semantic.{kind.value}", Library.PYCRYPTODOME, kind, "ANY", q, "D5" if is_signer else "D9", snippet)
            ev = SiteEvidence(cand, kind.value, receiver=receiver_info(t), function=fn.qualname if fn else None,
                              cls=fn.cls.name if fn and fn.cls else None, hybrid_context=hybrid_for(fn, node.lineno))
            ev.args.padding = t.scheme if isinstance(t, (SignerObject, CipherObject)) else None
            out.append(ev); seen.add(key)
            continue
        # ---- PQC presence
        if q and q.startswith(PQC_PREFIXES):
            cand = Candidate(_loc(rel_path, node), "semantic.pqc", Library.PYCA if q.startswith("cryptography") else Library.UNKNOWN,
                             CandidateKind.PQC_PRESENCE, "ML-KEM" if "mlkem" in q or "KeyEncapsulation" in q else "ML-DSA", q, "C24", snippet)
            out.append(SiteEvidence(cand, "pqc", function=fn.qualname if fn else None, cls=fn.cls.name if fn and fn.cls else None, hybrid_context=True))
            seen.add(key)
            continue
        # ---- operations: <recv>.sign/verify/exchange/encrypt/decrypt(...)
        if isinstance(node.func, ast.Attribute) and node.func.attr in OPERATION_METHODS:
            if isinstance(node.func.value, ast.Name) and fn is not None:
                recv_t = typer.type_of_name_at(node.func.value.id, fn, node)   # branch-aware at the use site
            else:
                recv_t = typer.type_of_expr(node.func.value, fn)
            info = receiver_info(recv_t)
            lib = Library.PYCRYPTODOME if info.library == "pycryptodome" else (Library.PYCA if info.library == "pyca" else Library.UNKNOWN)
            cand = Candidate(_loc(rel_path, node), "semantic.operation", lib, CandidateKind.OPERATION, info.algorithm or "ANY",
                             f"<receiver>.{node.func.attr}", "C3-C14", snippet)
            kind = "operation"
            if isinstance(recv_t, Unknown) and recv_t.reason == "non-public-key object":
                kind = "not-public-key"
            if isinstance(recv_t, Unknown) and recv_t.reason == "pqc object":
                kind = "pqc"          # ML-KEM / ML-DSA operation: evidence for hybrids, never a classical site
            ev = SiteEvidence(cand, kind, operation=node.func.attr, receiver=info, function=fn.qualname if fn else None,
                              cls=fn.cls.name if fn and fn.cls else None, hybrid_context=hybrid_for(fn, node.lineno))
            ev.args = resolve_args(node, typer, fn, recv_t)
            if ev.args.ecdsa and info.algorithm not in (None, "ANY", "EC"):
                ev.conflicts.append(f"ECDSA argument on a {info.algorithm} receiver")
            if ev.args.ecdh and info.algorithm not in (None, "ANY", "EC"):
                ev.conflicts.append(f"ECDH argument on a {info.algorithm} receiver")
            if ev.args.padding in ("PKCS1v15", "PSS", "OAEP") and info.algorithm not in (None, "ANY", "RSA"):
                ev.conflicts.append(f"RSA padding on a {info.algorithm} receiver")
            op = node.func.attr
            if op in ("sign", "verify") and ev.args.ecdh:
                ev.conflicts.append("ECDH argument on a signature operation")
            if op in ("sign", "verify") and ev.args.padding == "OAEP":
                ev.conflicts.append("OAEP (encryption) padding on a signature operation")
            if op == "exchange" and (ev.args.ecdsa or ev.args.padding in ("PKCS1v15", "PSS", "OAEP")):
                ev.conflicts.append("signature/encryption argument on a key-agreement operation")
            if op in ("encrypt", "decrypt") and (ev.args.ecdsa or ev.args.ecdh or ev.args.padding == "PSS"):
                ev.conflicts.append("signature or key-agreement argument on an encryption operation")
            if ev.hybrid_context and node.func.attr in ("exchange", "sign", "verify"):
                ev.hybrid_combined = combined_hybrid(typer, node, fn, node.func.attr)
            if "assumed-same-class" in (info.via_call or ""):
                ev.notes.append("receiver attribute resolved by assuming the same class")
            out.append(ev); seen.add(key)
    # operations inherit the consistency of the key-material sites their receiver was traced to
    km_by_line: dict[int, list[SiteEvidence]] = {}
    for e in out:
        if e.site_kind == "key-material":
            km_by_line.setdefault(e.candidate.location.line, []).append(e)
    for e in out:
        if e.site_kind != "operation":
            continue
        fams: set[str] = set()
        for line, _ in e.receiver.origins:
            for km in km_by_line.get(line, []):
                fams |= km.consumers.families
                e.origin_conflict = e.origin_conflict or bool(km.consumers.conflicts)
        e.origin_families = sorted(fams)
        if e.conflicts:
            for line, _ in e.receiver.origins:
                for km in km_by_line.get(line, []):
                    km.consumers.conflict(f"operation at line {e.candidate.location.line} has conflicting arguments: {e.conflicts[0]}")
    ops_by_line: dict[int, list[SiteEvidence]] = {}
    for e in out:
        if e.site_kind == "operation":
            ops_by_line.setdefault(e.candidate.location.line, []).append(e)
    for e in out:
        if e.site_kind == "key-material" and e.consumers.locations:
            consumer_ops = [o for line, _ in e.consumers.locations for o in ops_by_line.get(line, [])]
            e.hybrid_combined = bool(consumer_ops) and all(o.hybrid_combined for o in consumer_ops)
    for e in out:
        line = e.candidate.location.line
        fn = typer.function_at(line)
        cls = fn.cls if fn else typer.class_of_line(line)
        scope = cls if cls is not None else (fn.node if fn else None)
        if scope is not None:
            e.hybrid_apis = sorted({q for l, q in pqc_calls if scope.lineno <= l <= (scope.end_lineno or scope.lineno)})
    out.sort(key=lambda e: (e.candidate.location.line, e.candidate.location.col))
    return out
