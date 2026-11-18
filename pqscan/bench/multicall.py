"""Multi-call candidate statements (owner decision F03; annotation guide v1.2 Step A "Multi-call candidate statement").

The candidate pool is deduplicated by statement (protocol V6, unchanged), while a site is one call expression (role
taxonomy rule 7). For the few candidate statements that contain more than one call to a supported cryptographic API,
the guide fixes which call is the candidate's site. This module only LISTS the calls of a statement, by API name and in
source order, so that the issued to-do entry can be marked `multi_call` and the owner can apply the rule. It never
decides a role, eligibility or the site: those stay with the owner. It reads source text only, never tool output.

Names (receiver types are not resolved, so a builder method called `public_key` is listed too):
  operation:    sign, verify, exchange, encrypt, decrypt
  key_material: generate_private_key, import_key, construct, public_key, from_private_bytes, from_public_bytes,
                from_encoded_point, private_numbers, public_numbers, load_pem_* / load_der_* / load_ssh_*,
                RSA/ECC/DSA.generate
  constructor:  PKCS1_OAEP / PKCS1_v1_5 / pkcs1_15 / pss / DSS .new
"""
from __future__ import annotations

import ast

OPERATIONS = frozenset({"sign", "verify", "exchange", "encrypt", "decrypt"})
KEY_MATERIAL = frozenset({"generate_private_key", "import_key", "construct", "public_key", "from_private_bytes",
                          "from_public_bytes", "from_encoded_point", "private_numbers", "public_numbers"})
KEY_PREFIXES = ("load_pem_", "load_der_", "load_ssh_")
GENERATE_RECEIVERS = frozenset({"RSA", "ECC", "DSA"})
CONSTRUCTOR_RECEIVERS = frozenset({"PKCS1_OAEP", "PKCS1_v1_5", "pkcs1_15", "pss", "DSS"})


def call_kind(call: ast.Call) -> str | None:
    """'operation' / 'key_material' / 'constructor' for a supported API name, else None."""
    f = call.func
    if isinstance(f, ast.Attribute):
        name, recv = f.attr, (f.value.id if isinstance(f.value, ast.Name) else None)
    elif isinstance(f, ast.Name):
        name, recv = f.id, None
    else:
        return None
    if name in OPERATIONS:
        return "operation"
    if name in KEY_MATERIAL or name.startswith(KEY_PREFIXES) or (name == "generate" and recv in GENERATE_RECEIVERS):
        return "key_material"
    if name == "new" and recv in CONSTRUCTOR_RECEIVERS:
        return "constructor"
    return None


def _statement_at(tree: ast.AST, line: int) -> ast.stmt | None:
    best = None
    for n in ast.walk(tree):
        if isinstance(n, ast.stmt) and n.lineno == line:
            if best is None or (n.end_lineno - n.lineno) < (best.end_lineno - best.lineno):
                best = n
    return best


def statement_calls(text: str, line: int) -> list[dict] | None:
    """Supported-API calls of the statement that starts at `line` (header only for compound statements), in source
    order (line, column of the called name). None if the file does not parse or no statement starts there."""
    try:
        tree = ast.parse(text)
    except (SyntaxError, ValueError):
        return None
    node = _statement_at(tree, line)
    if node is None:
        return None
    body = {id(x) for fld in ("body", "orelse", "finalbody", "handlers")
            for c in (getattr(node, fld, None) or []) for x in ast.walk(c)}
    out = []
    for c in ast.walk(node):
        if isinstance(c, ast.Call) and id(c) not in body:
            k = call_kind(c)
            if k:
                f = c.func
                name = f.attr if isinstance(f, ast.Attribute) else f.id
                pos = (f.end_lineno, f.end_col_offset - len(name)) if isinstance(f, ast.Attribute) else (f.lineno, f.col_offset)
                out.append({"line": pos[0], "col": pos[1], "name": name, "kind": k})
    return sorted(out, key=lambda d: (d["line"], d["col"], d["name"]))


def mark(text: str, line: int) -> dict:
    """Fields added to an issued to-do entry: {'multi_call': bool, 'calls': [...]} (calls only when multi_call)."""
    calls = statement_calls(text, line) or []
    return {"multi_call": True, "calls": calls} if len(calls) > 1 else {"multi_call": False}
