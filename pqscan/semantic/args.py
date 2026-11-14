"""Argument resolution for operation calls: padding, hash, ECDSA/ECDH wrappers, curve, key size."""
from __future__ import annotations
import ast
from dataclasses import dataclass, field
from .model import AbstractType, ParamType, Multi, Unknown, SignerObject, CipherObject, describe
from .typer import ModuleTyper, FunctionCtx


@dataclass
class ArgEvidence:
    padding: str | None = None       # PKCS1v15 | PSS | OAEP | pkcs1_15 | pss | PKCS1_OAEP | ... | multi{...} | None
    hash: str | None = None
    ecdsa: bool = False
    ecdh: bool = False
    curve: str | None = None
    unresolved: list[str] = field(default_factory=list)   # argument texts that could not be typed
    resolved_all: bool = True

    def summary(self) -> str:
        parts = []
        if self.padding: parts.append(f"padding={self.padding}")
        if self.hash: parts.append(f"hash={self.hash}")
        if self.ecdsa: parts.append("ECDSA")
        if self.ecdh: parts.append("ECDH")
        if self.curve: parts.append(f"curve={self.curve}")
        return ", ".join(parts) or "no parameters"


def _param_names(t: AbstractType, kind: str) -> list[str]:
    if isinstance(t, ParamType) and t.kind == kind:
        return [t.name]
    if isinstance(t, Multi):
        names: list[str] = []
        for o in t.options:
            names += _param_names(o, kind)
        return names
    return []


def _collect(node: ast.AST, typer: ModuleTyper, fn: FunctionCtx | None, ev: ArgEvidence) -> None:
    """Type `node` and its nested call arguments (e.g. MGF1 inside PSS, SHA256 inside ECDSA)."""
    t = typer.type_of_expr(node, fn)
    pads, hashes, sig, kex, curves = _param_names(t, "padding"), _param_names(t, "hash"), _param_names(t, "sigalg"), _param_names(t, "kex"), _param_names(t, "curve")
    if pads:
        ev.padding = pads[0] if len(set(pads)) == 1 else "multi{" + "|".join(sorted(set(pads))) + "}"
    if hashes and ev.hash is None:
        ev.hash = hashes[0] if len(set(hashes)) == 1 else "multi{" + "|".join(sorted(set(hashes))) + "}"
    if sig:
        ev.ecdsa = True
    if kex:
        ev.ecdh = True
    if curves and ev.curve is None:
        ev.curve = curves[0]
    if isinstance(t, Unknown) and not isinstance(node, ast.Constant):
        # data arguments (message, signature bytes) are expected to be unknown; only record
        # unresolved *parameter-looking* arguments (attribute chains / calls)
        if isinstance(node, (ast.Attribute, ast.Call)):
            ev.unresolved.append(f"{type(node).__name__} argument")   # kind only: never source text
            ev.resolved_all = False
    if isinstance(node, ast.Call):
        for a in node.args:
            _collect(a, typer, fn, ev)
        for kw in node.keywords:
            _collect(kw.value, typer, fn, ev)


def resolve_args(call: ast.Call, typer: ModuleTyper, fn: FunctionCtx | None, receiver: AbstractType | None = None) -> ArgEvidence:
    ev = ArgEvidence()
    for a in call.args:
        _collect(a, typer, fn, ev)
    for kw in call.keywords:
        _collect(kw.value, typer, fn, ev)
    # PyCryptodome: the scheme lives on the signer/cipher object, not in the call arguments
    if isinstance(receiver, SignerObject) and receiver.scheme:
        ev.padding = receiver.scheme
    if isinstance(receiver, CipherObject) and receiver.scheme:
        ev.padding = receiver.scheme
    return ev
