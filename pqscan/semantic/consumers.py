"""Bounded consumer tracing for key material.

Given the call that produces a key (keygen / loader / construct) we follow the value through:
  * the variable it is assigned to, inside the same function (flow-insensitive);
  * aliases (`k2 = k`, `k = k.public_key()`), tracked with a visited set rather than a depth budget;
  * `self.attr = value`, then every method of the class (`self.attr.<op>()`, `k = self.attr`);
  * tuple-packed key pairs passed to a parameter and unpacked there (`vals=(priv, pub)` ->
    `self.a, self.b = vals`);
  * at most two levels of call that leave the current class (to a module-level function or another
    class defined in the same module: parameter binding, then the same rules inside the callee; for a
    class, its `__init__`), and the same two levels back from a `return` to in-module call sites.
    Hops that stay inside one class (`self.helper(k)`, `self.__class__(k)`, a private helper returning
    to a sibling method) do not consume that budget, because attribute tracing is already class-wide;
    they are cycle-protected by the visited set;
  * PyCryptodome signer/cipher constructors (`pkcs1_15.new(k)` -> signature family, etc.);
  * a public key passed as the peer argument of `<other>.exchange(..., key)` (key agreement).
Escapes (returned from a public function, passed to an unresolved callee, stored outside the
class) are recorded, never guessed through.
"""
from __future__ import annotations
import ast
from dataclasses import dataclass, field
from .apis import (OPERATION_METHODS, FAMILY_OF_METHOD, SIGNER_MODULES, CIPHER_MODULES, NON_PK_OBJECTS,
                   KEY_FACTORIES, CERT_LOADERS)
from .typer import ModuleTyper, FunctionCtx, dotted
from .branches import exclusive_branches as _exclusive_branches
from .model import KeyType, CertType, Multi, Unknown, Instance, ParamType, SignerObject, CipherObject

MAX_CALL_DEPTH = 2
# operations a key of each algorithm can perform (taxonomy rule 1: only type-valid consumers count).
# "signer"/"cipher" are PyCryptodome Signature.*.new(key) / Cipher.PKCS1_*.new(key).
VALID_OPS = {
    "RSA": {"sign", "verify", "encrypt", "decrypt", "signer", "cipher"},
    "EC": {"sign", "verify", "exchange", "signer"},
    "X25519": {"exchange"}, "X448": {"exchange"}, "XDH": {"exchange"}, "DH": {"exchange"},
    "Ed25519": {"sign", "verify", "signer"}, "Ed448": {"sign", "verify", "signer"}, "EdDSA": {"sign", "verify", "signer"},
    "DSA": {"sign", "verify", "signer"},
}
HARMLESS_BUILTINS = {"isinstance", "type", "id", "print", "len", "repr", "str", "hash", "bool", "getattr", "hasattr"}


@dataclass
class ConsumerEvidence:
    families: set[str] = field(default_factory=set)          # subset of {"SIG", "KE", "PKE"}
    locations: list[tuple[int, str]] = field(default_factory=list)   # (line, description)
    paths: list[str] = field(default_factory=list)            # human-readable trace paths
    escapes: bool = False
    escape_notes: list[str] = field(default_factory=list)
    unresolved_callees: list[str] = field(default_factory=list)
    conflicts: list[str] = field(default_factory=list)       # impossible consumers, incompatible rebinding
    filtered: list[str] = field(default_factory=list)        # consumers dropped by taxonomy rule 1 (wrong key half)

    def conflict(self, note: str) -> None:
        if note not in self.conflicts:
            self.conflicts.append(note)

    def add(self, family: str, line: int, desc: str, path: str) -> None:
        self.families.add(family)
        if (line, desc) not in self.locations:
            self.locations.append((line, desc))
        self.paths.append(path)

    def escape(self, note: str) -> None:
        self.escapes = True
        if note not in self.escape_notes:
            self.escape_notes.append(note)


def _enclosing_stmt(fn_node: ast.AST, target: ast.AST) -> ast.stmt | None:
    best: ast.stmt | None = None
    for node in ast.walk(fn_node):
        if isinstance(node, ast.stmt) and node.lineno <= target.lineno <= (node.end_lineno or node.lineno):
            if best is None or node.lineno >= best.lineno:
                if any(n is target for n in ast.walk(node)):
                    best = node
    return best


def _value_parts(v: ast.AST | None) -> list[ast.AST]:
    """The alternatives a value expression can evaluate to: `a if c else b` -> [a, b]; `a or b` -> [a, b]."""
    if isinstance(v, ast.IfExp):
        return _value_parts(v.body) + _value_parts(v.orelse)
    if isinstance(v, ast.BoolOp) and isinstance(v.op, ast.Or):
        return [x for e in v.values for x in _value_parts(e)]
    return [v] if v is not None else []


def _direct_value_of(stmt: ast.stmt, call: ast.Call) -> bool:
    for v in _value_parts(getattr(stmt, "value", None)):
        if v is call:
            return True
        # k = <call>.public_key()  /  k = <call>.publickey()
        if isinstance(v, ast.Call) and isinstance(v.func, ast.Attribute) and v.func.value is call and v.func.attr in ("public_key", "publickey", "private_key"):
            return True
    return False


def _is_property(fn: FunctionCtx) -> bool:
    return any(dotted(d) in ("property", "functools.cached_property", "cached_property") for d in fn.node.decorator_list)


class ConsumerTracer:
    def __init__(self, typer: ModuleTyper):
        self.t = typer
        self._visited: set[tuple] = set()
        self._origin: ast.AST | None = None
        self._origin_alg = "ANY"
        self._origin_private: bool | None = None
        self._carriers: set[int] = set()        # ids of call nodes whose result is the traced value

    # ------------------------------------------------------------------ entry
    def trace(self, call: ast.Call, fn: FunctionCtx | None) -> ConsumerEvidence:
        ev = self._trace(call, fn)
        # rule 1 filtering is silent when valid consumers remain; if nothing valid is left the code is
        # contradictory for this key (e.g. a public key only ever used to sign): report a conflict
        if ev.filtered and not ev.families:
            for f in ev.filtered:
                ev.conflict(f)
        return ev

    def _trace(self, call: ast.Call, fn: FunctionCtx | None) -> ConsumerEvidence:
        self._visited = set()
        self._carriers = set()
        self._origin = call
        t = self.t.type_of_expr(call, fn) if fn is not None else None
        self._origin_alg = t.algorithm if isinstance(t, KeyType) else "ANY"
        self._origin_private = t.private if isinstance(t, KeyType) else (False if isinstance(t, CertType) else None)
        ev = ConsumerEvidence()
        if fn is None:
            ev.escape("module-level key material")
            return ev
        stmt = _enclosing_stmt(fn.node, call)
        if stmt is None:
            ev.escape("no enclosing statement")
            return ev
        path = f"{fn.qualname}:{call.lineno}"
        if isinstance(stmt, (ast.Assign, ast.AnnAssign)) and _direct_value_of(stmt, call):
            targets = stmt.targets if isinstance(stmt, ast.Assign) else [stmt.target]
            for tgt in targets:
                self._bind_target(tgt, fn, ev, path, depth=0)
        elif isinstance(stmt, ast.Expr) and stmt.value is call:
            pass   # result discarded (e.g. a capability probe `X25519PrivateKey.generate()`): no consumer, no escape
        elif isinstance(stmt, ast.Return) and stmt.value is not None and (stmt.value is call or _direct_value_of(stmt, call)):
            self._follow_return(fn, ev, path, depth=0)
        else:
            # the call is nested in another expression (argument of a call, receiver of an op, ...)
            self._uses_of_expr_node(call, fn, ev, path, depth=0)
        return ev

    # ------------------------------------------------------------------ helpers
    def _bind_target(self, tgt: ast.AST, fn: FunctionCtx, ev: ConsumerEvidence, path: str, depth: int) -> None:
        if isinstance(tgt, ast.Name):
            self._uses_of_name(tgt.id, fn, ev, path, depth)
        elif isinstance(tgt, ast.Attribute) and fn.self_name and isinstance(tgt.value, ast.Name) and tgt.value.id == fn.self_name and fn.cls is not None:
            self._uses_of_attr(fn.cls, tgt.attr, ev, f"{path} -> self.{tgt.attr}", depth)
        else:
            ev.escape(f"stored in a {type(tgt).__name__.lower()} target outside the analysed scope")

    def _uses_of_expr_node(self, node: ast.AST, fn: FunctionCtx, ev: ConsumerEvidence, path: str, depth: int) -> None:
        """The key expression appears inside a larger expression: find the immediately enclosing use."""
        for parent in ast.walk(fn.node):
            if isinstance(parent, ast.Call) and isinstance(parent.func, ast.Attribute) and parent.func.value is node \
                    and parent.func.attr in ("public_key", "publickey"):
                self._uses_of_expr_node(parent, fn, ev, path, depth)   # keygen(...).public_key().<op>(...)
                return
            if isinstance(parent, ast.Call) and isinstance(parent.func, ast.Attribute) and parent.func.value is node and parent.func.attr in OPERATION_METHODS:
                self._consume(ev, parent.func.attr, FAMILY_OF_METHOD[parent.func.attr], parent.lineno, f".{parent.func.attr}()", f"{path} -> .{parent.func.attr}():{parent.lineno}")
                return
            if isinstance(parent, ast.Call) and (any(a is node for a in parent.args) or any(k.value is node for k in parent.keywords)):
                self._key_passed_to_call(parent, node, fn, ev, path, depth)
                return
            if isinstance(parent, (ast.Tuple, ast.List)) and any(e is node for e in parent.elts):
                for grand in ast.walk(fn.node):
                    if isinstance(grand, ast.Call) and (any(a is parent for a in grand.args) or any(k.value is parent for k in grand.keywords)):
                        idx = [i for i, e in enumerate(parent.elts) if e is node]
                        self._key_passed_to_call(grand, parent, fn, ev, path, depth, indices=idx)
                        return
        ev.escape("used in an unsupported expression")

    @staticmethod
    def _is_name(node: ast.AST, name: str) -> bool:
        return isinstance(node, ast.Name) and node.id == name

    @staticmethod
    def _is_self_attr(node: ast.AST, fn: FunctionCtx, attr: str) -> bool:
        return (isinstance(node, ast.Attribute) and node.attr == attr and isinstance(node.value, ast.Name)
                and fn.self_name is not None and node.value.id == fn.self_name)

    def _is_sibling_attr(self, node: ast.AST, fn: FunctionCtx, attr: str, cls: ast.ClassDef) -> bool:
        """`self.public_key().<attr>` where the method returns an instance of the same class
        (e.g. `return self.__class__(self.prepared_key.public_key())`): the same attribute slot."""
        if not (isinstance(node, ast.Attribute) and node.attr == attr and isinstance(node.value, ast.Call)):
            return False
        t = self.t.type_of_expr(node.value, fn)
        opts = t.options if isinstance(t, Multi) else (t,)
        return any(isinstance(o, Instance) and o.cls_name == cls.name for o in opts)

    def _uses_of_name(self, name: str, fn: FunctionCtx, ev: ConsumerEvidence, path: str, depth: int) -> None:
        key = ("name", fn.qualname, name)
        if key in self._visited:
            return
        self._visited.add(key)
        self._scan_uses(lambda n: self._is_name(n, name), fn, ev, f"{path} -> {name}", depth)

    def _uses_of_attr(self, cls: ast.ClassDef, attr: str, ev: ConsumerEvidence, path: str, depth: int) -> None:
        key = ("attr", cls.name, attr)
        if key in self._visited:
            return
        self._visited.add(key)
        for sub in cls.body:
            if isinstance(sub, (ast.FunctionDef, ast.AsyncFunctionDef)):
                mctx = self.t.functions.get(f"{cls.name}.{sub.name}")
                if mctx and mctx.self_name:
                    self._scan_uses(lambda n, m=mctx: self._is_self_attr(n, m, attr) or self._is_sibling_attr(n, m, attr, cls),
                                    mctx, ev, f"{path} in {mctx.qualname}", depth)

    def _uses_of_container(self, param: str, indices: list[int], fn: FunctionCtx, ev: ConsumerEvidence, path: str, depth: int) -> None:
        """`param` holds a tuple whose elements `indices` are the traced key: follow tuple unpacking."""
        key = ("container", fn.qualname, param, tuple(indices))
        if key in self._visited:
            return
        self._visited.add(key)
        unpacked = False
        for node in ast.walk(fn.node):
            if isinstance(node, ast.Assign) and self._is_name(node.value, param):
                for tgt in node.targets:
                    if isinstance(tgt, (ast.Tuple, ast.List)):
                        unpacked = True
                        for i in indices:
                            if i < len(tgt.elts):
                                self._bind_target(tgt.elts[i], fn, ev, f"{path} -> {param}[{i}]", depth)
            if isinstance(node, ast.Subscript) and self._is_name(node.value, param) and isinstance(node.slice, ast.Constant) and node.slice.value in indices:
                unpacked = True
                self._uses_of_expr_node(node, fn, ev, f"{path} -> {param}[{node.slice.value}]", depth)
        if not unpacked:
            ev.escape(f"tuple parameter {param} of {fn.qualname} not unpacked in a supported way")

    @staticmethod
    def _strip_public_key(node: ast.AST, matches) -> ast.AST:
        """`<match>.public_key()` -> `<match>` (the public half belongs to the same key pair)."""
        if (isinstance(node, ast.Call) and isinstance(node.func, ast.Attribute)
                and node.func.attr in ("public_key", "publickey") and matches(node.func.value)):
            return node.func.value
        return node

    def _scan_uses(self, matches, fn: FunctionCtx, ev: ConsumerEvidence, path: str, depth: int) -> None:
        m = lambda n: matches(self._strip_public_key(n, matches))  # noqa: E731
        branchy = self._origin is not None and any(isinstance(x, (ast.If, ast.Try)) for x in ast.walk(fn.node)) \
            and any(x is self._origin for x in ast.walk(fn.node))
        for node in ast.walk(fn.node):
            if branchy and isinstance(node, ast.Call) and _exclusive_branches(fn.node, self._origin, node):
                continue                     # a use in a branch that cannot run together with the key's creation
            if isinstance(node, ast.Call):
                # <key>.<op>(...)  and  <key>.public_key().<op>(...)
                if isinstance(node.func, ast.Attribute) and m(node.func.value):
                    if node.func.attr in OPERATION_METHODS:
                        self._consume(ev, node.func.attr, FAMILY_OF_METHOD[node.func.attr], node.lineno, f".{node.func.attr}()", f"{path} -> .{node.func.attr}():{node.lineno}")
                    continue
                # peer public key of a key agreement: <other>.exchange(..., key)
                if isinstance(node.func, ast.Attribute) and node.func.attr == "exchange" and (
                        any(m(a) for a in node.args) or any(m(k.value) for k in node.keywords)):
                    self._consume(ev, "exchange", "KE", node.lineno, "peer key of .exchange()", f"{path} -> peer of .exchange():{node.lineno}", peer=True)
                    continue
                # passed as an argument, directly or inside a tuple/list literal
                arg_node = next((a for a in node.args if m(a)), None) or next((k.value for k in node.keywords if m(k.value)), None)
                if arg_node is not None:
                    self._key_passed_to_call(node, arg_node, fn, ev, path, depth)
                    continue
                for a in list(node.args) + [k.value for k in node.keywords]:
                    if isinstance(a, (ast.Tuple, ast.List)):
                        idx = [i for i, e in enumerate(a.elts) if m(e)]
                        if idx:
                            self._key_passed_to_call(node, a, fn, ev, path, depth, indices=idx)
                continue
            # rebinding: the traced name/attribute is assigned a value that does not come from the traced key
            if isinstance(node, ast.Assign) and any(matches(t) for t in node.targets) and not any(m(v) for v in _value_parts(node.value)):
                self._check_rebinding(node, fn, ev, matches)
                continue
            # alias:  x = <match>   /  x = <match>.public_key()
            if isinstance(node, ast.Assign) and len(node.targets) == 1 and any(m(v) for v in _value_parts(node.value)):
                tgt = node.targets[0]
                if matches(tgt):
                    continue  # `key = key.public_key()`: same variable, already being traced
                self._bind_target(tgt, fn, ev, path, depth)
                continue
            if isinstance(node, ast.Return) and node.value is not None:
                vals = node.value.elts if isinstance(node.value, (ast.Tuple, ast.List)) else [node.value]
                if any(m(v) for v in vals):
                    if isinstance(node.value, (ast.Tuple, ast.List)):
                        ev.escape(f"returned inside a tuple from {fn.qualname} (line {node.lineno})")
                    else:
                        self._follow_return(fn, ev, path, depth)

    # ------------------------------------------------------------------ type validity and rebinding
    def _consume(self, ev: ConsumerEvidence, op: str, family: str, line: int, desc: str, path: str, peer: bool = False) -> None:
        """Record a consumer only if the traced key can perform it (taxonomy rule 1); otherwise a conflict."""
        alg, priv = self._origin_alg, self._origin_private
        valid = VALID_OPS.get(alg)
        reason = None
        if valid is not None and op not in valid:
            reason = f"a {alg} key cannot be used for {desc}"
        elif priv is False and not peer and op in ("sign", "decrypt", "exchange"):
            # taxonomy rule 1: only consumers that can succeed for this key half count
            note = f"a public key cannot be used for {desc} (line {line}); consumer not counted"
            if note not in ev.filtered:
                ev.filtered.append(note)
            return
        if reason:
            ev.conflict(f"{reason} (line {line}); the consumer belongs to another value (flow-insensitive name reuse)")
            return
        ev.add(family, line, desc, path)

    def _check_rebinding(self, node: ast.Assign, fn: FunctionCtx, ev: ConsumerEvidence, matches) -> None:
        if self._origin is not None and any(n is self._origin for n in ast.walk(node.value)):
            return                                   # the traced key's own binding
        if self._origin is not None and _exclusive_branches(fn.node, self._origin, node):
            return                                   # assigned in a mutually exclusive branch (if/else, try/except)
        if isinstance(node.value, ast.Constant):
            return                                   # `self.key = None` placeholders
        if any(matches(n) for n in ast.walk(node.value)):
            return                                   # derived from the traced value itself
        if any(id(n) in self._carriers for n in ast.walk(node.value)):
            return                                   # receives the traced value from a followed return
        if any(isinstance(n, ast.Name) and ("name", fn.qualname, n.id) in self._visited for n in ast.walk(node.value)):
            return                                   # a name already known to carry the traced value (e.g. the parameter it arrived in)
        ot = self.t.type_of_expr(node.value, fn)
        opts = ot.options if isinstance(ot, Multi) else (ot,)
        keys = [o for o in opts if isinstance(o, KeyType)]
        if keys:
            algs = {k.algorithm for k in keys} - {"ANY"}
            if self._origin_alg != "ANY" and algs and not algs <= {self._origin_alg}:
                ev.conflict(f"the name is rebound to a {'/'.join(sorted(algs))} key at line {node.lineno}; "
                            "flow-insensitive consumers may belong to that key")
            return                                   # an alternative key of the same algorithm: consumers are shared
        if any(isinstance(o, (Instance, ParamType, SignerObject, CipherObject, CertType)) for o in opts) or any(
                isinstance(o, Unknown) and o.reason in ("non-public-key object", "pqc object") for o in opts):
            ev.conflict(f"the name is rebound to a non-key object at line {node.lineno}; consumers may belong to it")
            return
        ev.escape(f"the name is rebound to an unresolved value at line {node.lineno}")

    # ------------------------------------------------------------------ calls in both directions
    def _call_sites_of(self, fn: FunctionCtx) -> list[ast.Call]:
        out: list[ast.Call] = []
        for node in ast.walk(self.t.tree):
            if not isinstance(node, ast.Call):
                continue
            f = node.func
            if fn.cls is None:
                if isinstance(f, ast.Name) and f.id == fn.name:
                    out.append(node)
            elif isinstance(f, ast.Attribute) and f.attr == fn.name and isinstance(f.value, ast.Name):
                caller = self.t.function_at(node.lineno)
                receivers = {fn.cls.name, "cls"} | ({caller.self_name} if caller and caller.self_name and caller.cls is fn.cls else set())
                if f.value.id in receivers:
                    out.append(node)
        return out

    def _follow_return(self, fn: FunctionCtx, ev: ConsumerEvidence, path: str, depth: int) -> None:
        key = ("return", fn.qualname)
        if key in self._visited:
            return
        self._visited.add(key)
        public = _is_property(fn) or not fn.name.startswith("_")
        sites = [] if _is_property(fn) else self._call_sites_of(fn)
        if not sites or public:
            ev.escape(f"returned from {'public ' if public else ''}{fn.qualname}" + ("; external callers possible" if public else ""))
        for call in sites:
            caller = self.t.function_at(call.lineno)
            if caller is None:
                ev.escape(f"returned to module level from {fn.qualname}")
                continue
            hop = 0 if (fn.cls is not None and caller.cls is fn.cls) else 1
            if depth + hop > MAX_CALL_DEPTH:
                ev.escape(f"returned from {fn.qualname}; call depth limit")
                continue
            stmt = _enclosing_stmt(caller.node, call)
            self._carriers.add(id(call))
            p = f"{path} -> return to {caller.qualname}:{call.lineno}"
            if isinstance(stmt, (ast.Assign, ast.AnnAssign)) and _direct_value_of(stmt, call):
                for tgt in (stmt.targets if isinstance(stmt, ast.Assign) else [stmt.target]):
                    self._bind_target(tgt, caller, ev, p, depth + hop)
            elif isinstance(stmt, ast.Return) and stmt.value is call:
                self._follow_return(caller, ev, p, depth + hop)
            else:
                self._uses_of_expr_node(call, caller, ev, p, depth + hop)

    def _key_passed_to_call(self, call: ast.Call, arg: ast.AST, fn: FunctionCtx, ev: ConsumerEvidence, path: str, depth: int,
                            indices: list[int] | None = None) -> None:
        q = self.t.qualified(call.func, fn)
        callee_text = dotted(call.func) or "<computed callee>"   # identifiers only, never source text
        if q:
            if any(q.endswith(m + ".new") for m in SIGNER_MODULES) and q.startswith(("Crypto.", "Cryptodome.")):
                self._consume(ev, "signer", "SIG", call.lineno, f"{callee_text}(key)", f"{path} -> {callee_text}:{call.lineno}")
                return
            if any(q.endswith(m + ".new") for m in CIPHER_MODULES) and q.startswith(("Crypto.", "Cryptodome.")):
                self._consume(ev, "cipher", "PKE", call.lineno, f"{callee_text}(key)", f"{path} -> {callee_text}:{call.lineno}")
                return
            if q in NON_PK_OBJECTS:
                return
            if q in KEY_FACTORIES or q in CERT_LOADERS:
                # loaders take bytes; a traced key object can only reach one through variable reuse
                # (`key = load_pem_public_key(key)`), which flow-insensitive tracing over-approximates
                return
            ev.unresolved_callees.append(callee_text)
            ev.escape(f"passed to library call {callee_text} at line {call.lineno}")
            return
        target_cls = None
        if isinstance(call.func, ast.Name) and call.func.id in self.t.classes:
            target_cls = self.t.classes[call.func.id]
        elif fn.cls is not None and self.t.is_ctor_call(call, fn.cls):
            target_cls = fn.cls
        if isinstance(call.func, ast.Name) and call.func.id in HARMLESS_BUILTINS and target_cls is None:
            return
        target: FunctionCtx | None = None
        skip_self = False
        if target_cls is not None:
            target = self.t.functions.get(f"{target_cls.name}.__init__")
            skip_self = True
            if target is None:
                ev.escape(f"passed to class {target_cls.name} without __init__ (line {call.lineno})")
                return
        elif isinstance(call.func, ast.Name) and call.func.id in self.t.functions:
            target = self.t.functions[call.func.id]
        elif isinstance(call.func, ast.Attribute) and fn.cls is not None and isinstance(call.func.value, ast.Name) \
                and call.func.value.id in ({fn.self_name, "cls", fn.cls.name} - {None}):
            target = self.t.method_of(fn.cls, call.func.attr)
            skip_self = target is not None and target.self_name is not None
        if target is not None:
            hop = 0 if (fn.cls is not None and target.cls is fn.cls) else 1
            if depth + hop > MAX_CALL_DEPTH:
                ev.escape(f"call depth limit at {target.qualname} (line {call.lineno})")
                return
            param = self._bind_param(target, call, arg, skip_self=skip_self)
            if param:
                p = f"{path} -> {target.qualname}({param})"
                if indices is not None:
                    self._uses_of_container(param, indices, target, ev, p, depth + hop)
                else:
                    self._uses_of_name(param, target, ev, p, depth + hop)
                return
        ev.unresolved_callees.append(callee_text)
        ev.escape(f"passed to unresolved callee {callee_text} at line {call.lineno}")

    @staticmethod
    def _bind_param(target: FunctionCtx, call: ast.Call, arg: ast.AST, skip_self: bool) -> str | None:
        params = [a.arg for a in target.node.args.args]
        if skip_self and params:
            params = params[1:]
        for i, a in enumerate(call.args):
            if a is arg and i < len(params):
                return params[i]
        for k in call.keywords:
            if k.value is arg and k.arg in params + [a.arg for a in target.node.args.kwonlyargs]:
                return k.arg
        return None
