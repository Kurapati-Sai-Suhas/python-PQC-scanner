"""Flow-insensitive, bounded expression typing for one module.

Rules (documented limitations in docs/specification/api_coverage.md Sec. 3):
- a Name is typed from the set of assignments to it inside the function (unique -> that type,
  several distinct -> Multi); parameters from annotations or isinstance guards, else Unknown(parameter);
- `self.attr` is typed from all assignments to that attribute anywhere in the class (incl. class body);
- a call to a function defined in the same module is typed from that function's return statements
  (one level, no recursion); instantiating a local class yields Instance(class);
- everything else is Unknown with a reason.
"""
from __future__ import annotations
import ast
from dataclasses import dataclass, field
from .apis import (KEY_FACTORIES, NUMBERS_CLASSES, CERT_LOADERS, SIGNER_MODULES, CIPHER_MODULES,
                   KEY_CLASS_TYPES, NON_PK_OBJECTS, PQC_PREFIXES, PARAM_CONSTRUCTORS)
from .imports import ImportMap
from .model import AbstractType, KeyType, CertType, SignerObject, CipherObject, Multi, Unknown, Origin, ParamType, Instance
from ..models import Provenance


def dotted(node: ast.AST) -> str | None:
    """Return `a.b.c` for Name/Attribute chains, else None."""
    if isinstance(node, ast.Name):
        return node.id
    if isinstance(node, ast.Attribute):
        base = dotted(node.value)
        return f"{base}.{node.attr}" if base else None
    return None


@dataclass
class FunctionCtx:
    qualname: str                      # "f" or "Class.method"
    node: ast.FunctionDef | ast.AsyncFunctionDef
    cls: ast.ClassDef | None = None
    self_name: str | None = None

    @property
    def name(self) -> str:
        return self.node.name


class ModuleTyper:
    def __init__(self, tree: ast.Module, lines: list[str] | None = None):
        self.tree = tree
        self.lines = lines or []
        self.imports = ImportMap.from_module(tree)
        self.functions: dict[str, FunctionCtx] = {}
        self.classes: dict[str, ast.ClassDef] = {}
        self._index()
        self._cache: dict[tuple, AbstractType] = {}

    # ------------------------------------------------------------------ indexing
    def _module_level_defs(self) -> list[ast.stmt]:
        """Top-level statements, descending through module-level `if` / `try` / `with` blocks
        (e.g. `if has_crypto:` guards around whole class definitions), but never into functions."""
        out: list[ast.stmt] = []

        def visit(body: list[ast.stmt]) -> None:
            for s in body:
                if isinstance(s, (ast.If, ast.Try, ast.With)) or type(s).__name__ == "TryStar":
                    for fld in ("body", "orelse", "finalbody"):
                        visit(getattr(s, fld, []) or [])
                    for h in getattr(s, "handlers", []) or []:
                        visit(h.body)
                else:
                    out.append(s)
        visit(self.tree.body)
        return out

    def _index(self) -> None:
        for node in self._module_level_defs():
            if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
                self.functions[node.name] = FunctionCtx(node.name, node)
            elif isinstance(node, ast.ClassDef):
                self.classes[node.name] = node
                for sub in node.body:
                    if isinstance(sub, (ast.FunctionDef, ast.AsyncFunctionDef)):
                        decorators = {dotted(d) for d in sub.decorator_list}
                        # static and class methods have no instance receiver: their first parameter is not `self`
                        if decorators & {"staticmethod", "classmethod"}:
                            self_name = None
                        else:
                            self_name = sub.args.args[0].arg if sub.args.args else None
                        self.functions[f"{node.name}.{sub.name}"] = FunctionCtx(f"{node.name}.{sub.name}", sub, node, self_name)

    def function(self, qualname: str) -> FunctionCtx:
        return self.functions[qualname]

    def method_of(self, cls: ast.ClassDef, name: str, _seen: set[str] | None = None) -> FunctionCtx | None:
        """Find `name` on `cls`, then on base classes defined in this module (depth-first, cycle-safe)."""
        seen = _seen or set()
        if cls.name in seen:
            return None
        seen.add(cls.name)
        fn = self.functions.get(f"{cls.name}.{name}")
        if fn:
            return fn
        for b in cls.bases:
            base = self.classes.get(dotted(b) or "")
            if base is not None:
                found = self.method_of(base, name, seen)
                if found:
                    return found
        return None

    def function_at(self, line: int) -> FunctionCtx | None:
        """Innermost indexed function containing `line` (1-based)."""
        best = None
        for fn in self.functions.values():
            n = fn.node
            if n.lineno <= line <= (n.end_lineno or n.lineno):
                if best is None or n.lineno >= best.node.lineno:
                    best = fn
        return best

    def class_of_line(self, line: int) -> ast.ClassDef | None:
        for c in self.classes.values():
            if c.lineno <= line <= (c.end_lineno or c.lineno):
                return c
        return None

    def qualified(self, node: ast.AST, fn: FunctionCtx | None) -> str | None:
        d = dotted(node)
        return self.imports.resolve(d, fn.name if fn else None) if d else None

    # ------------------------------------------------------------------ typing entry points
    def type_of_name(self, name: str, fn: FunctionCtx) -> AbstractType:
        return self.type_of_expr(ast.Name(id=name, ctx=ast.Load()), fn)

    def type_of_expr(self, expr: ast.AST, fn: FunctionCtx | None, depth: int = 0) -> AbstractType:
        if depth > 6:
            return Unknown(reason="depth limit")
        if isinstance(expr, ast.Name):
            return self._type_of_local(expr.id, fn, depth)
        if isinstance(expr, ast.Attribute):
            # self.attr
            if fn and fn.self_name and isinstance(expr.value, ast.Name) and expr.value.id == fn.self_name and fn.cls is not None:
                return self._type_of_attribute(fn.cls, expr.attr, fn, depth)
            # instance.attr where instance is a local class instance
            base = self.type_of_expr(expr.value, fn, depth + 1)
            if isinstance(base, Instance) and base.cls_name in self.classes:
                return self._type_of_attribute(self.classes[base.cls_name], expr.attr, fn, depth)
            # fallback: `<unresolved>.attr` where `attr` is an attribute of the current class
            # (e.g. `self.public_key().prepared_key`): assume the same class, and say so
            if fn and fn.cls is not None and self._class_assigns_attr(fn.cls, expr.attr):
                t = self._type_of_attribute(fn.cls, expr.attr, fn, depth)
                t.via_call = (t.via_call or "") + "|assumed-same-class"
                return t
            return Unknown(reason="attribute of unresolved object")
        if isinstance(expr, ast.Subscript) and isinstance(expr.value, ast.Dict):
            return self._merge([self.type_of_expr(v, fn, depth + 1) for v in expr.value.values if v is not None])
        if isinstance(expr, ast.Call):
            return self._type_of_call(expr, fn, depth)
        if isinstance(expr, ast.Await):
            return self.type_of_expr(expr.value, fn, depth)
        if isinstance(expr, (ast.IfExp,)):
            a, b = self.type_of_expr(expr.body, fn, depth + 1), self.type_of_expr(expr.orelse, fn, depth + 1)
            return self._merge([a, b])
        return Unknown(reason="unsupported expression")

    # ------------------------------------------------------------------ names and parameters
    def _assignments_to(self, name: str, fn: FunctionCtx) -> list[tuple[ast.AST, bool]]:
        """All values assigned to `name` in the function, each with a flag telling whether the
        assignment is an unconditional statement directly in the function body."""
        top_level = {id(s) for s in fn.node.body}
        out: list[tuple[ast.AST, bool]] = []
        for node in ast.walk(fn.node):
            if isinstance(node, ast.Assign):
                for t in node.targets:
                    if isinstance(t, ast.Name) and t.id == name:
                        out.append((node.value, id(node) in top_level))
                    elif isinstance(t, ast.Tuple) and isinstance(node.value, ast.Tuple):
                        for te, ve in zip(t.elts, node.value.elts):
                            if isinstance(te, ast.Name) and te.id == name:
                                out.append((ve, id(node) in top_level))
            elif isinstance(node, (ast.AnnAssign, ast.AugAssign)) and isinstance(node.target, ast.Name) and node.target.id == name and getattr(node, "value", None) is not None:
                out.append((node.value, id(node) in top_level))
            elif isinstance(node, ast.With):
                for item in node.items:
                    if isinstance(item.optional_vars, ast.Name) and item.optional_vars.id == name:
                        out.append((item.context_expr, False))
        return out

    def type_of_name_at(self, name: str, fn: FunctionCtx, use: ast.AST) -> AbstractType:
        """Like type_of_name, but ignores assignments in branches mutually exclusive with `use`
        (if/else, try/except alternatives). Not cached; used for operation receivers."""
        from .branches import exclusive_branches
        assigns = [(v, top) for v, top in self._assignments_to(name, fn)]
        stmts = {id(v): st for st in ast.walk(fn.node) if isinstance(st, ast.Assign) for v in [st.value]}
        kept = [(v, top) for v, top in assigns if not (id(v) in stmts and exclusive_branches(fn.node, stmts[id(v)], use))]
        if len(kept) == len(assigns) or not kept:
            return self._type_of_local(name, fn, 0)
        types = [self.type_of_expr(v, fn, 1) for v, _ in kept if not self._mentions(v, name)]
        if self._is_parameter(name, fn) and not any(top for _, top in kept):
            types.append(self._type_of_parameter(name, fn))
        return self._merge(types) if types else self._type_of_local(name, fn, 0)

    def _is_parameter(self, name: str, fn: FunctionCtx) -> bool:
        a = fn.node.args
        return any(p.arg == name for p in a.posonlyargs + a.args + a.kwonlyargs)

    @staticmethod
    def _mentions(expr: ast.AST, name: str) -> bool:
        return any(isinstance(n, ast.Name) and n.id == name for n in ast.walk(expr))

    def _type_of_local(self, name: str, fn: FunctionCtx | None, depth: int) -> AbstractType:
        """Flow-insensitive: the union of every value the name can hold in the function.
        A parameter keeps its incoming value unless it is unconditionally reassigned at the top
        level of the body. Self-referential reassignments (`key = key.public_key()`) are typed
        against the union of the other definitions (one pass, no fixpoint)."""
        if fn is None:
            return Unknown(reason="module-level name")
        key = ("local", fn.qualname, name)
        if key in self._cache:
            return self._cache[key]
        self._cache[key] = Unknown(reason="recursive")
        assigns = self._assignments_to(name, fn)
        plain = [v for v, _ in assigns if not self._mentions(v, name)]
        self_ref = [v for v, _ in assigns if self._mentions(v, name)]
        types = [self.type_of_expr(v, fn, depth + 1) for v in plain]
        if self._is_parameter(name, fn) and not any(top for v, top in assigns if not self._mentions(v, name)):
            types.append(self._type_of_parameter(name, fn))
        if not types and not self_ref:
            result = self._type_of_parameter(name, fn)
        else:
            base = self._merge(types) if types else Unknown(reason="no assignments")
            if self_ref:
                self._cache[key] = base
                types += [self.type_of_expr(v, fn, depth + 1) for v in self_ref]
            result = self._merge(types)
        self._cache[key] = result
        return result

    def _type_of_parameter(self, name: str, fn: FunctionCtx) -> AbstractType:
        args = fn.node.args
        all_params = args.posonlyargs + args.args + args.kwonlyargs
        for a in all_params:
            if a.arg == name:
                if a.annotation is not None:
                    q = self.qualified(a.annotation, fn)
                    if q in KEY_CLASS_TYPES:
                        alg, priv = KEY_CLASS_TYPES[q]
                        return KeyType(algorithm=alg, private=priv, provenance=Provenance.PARAMETER, proximate=Provenance.PARAMETER,
                                       library="pycryptodome" if q.startswith(("Crypto.", "Cryptodome.")) else "pyca",
                                       origins=(Origin(a.lineno, a.col_offset, f"annotation {q}"),))
                guard = self._isinstance_guard(name, fn)
                if guard:
                    return guard
                return Unknown(reason="untyped parameter", proximate=Provenance.PARAMETER)
        return Unknown(reason="undefined name")

    def _isinstance_guard(self, name: str, fn: FunctionCtx) -> AbstractType | None:
        found: list[AbstractType] = []
        for node in ast.walk(fn.node):
            if isinstance(node, ast.Call) and isinstance(node.func, ast.Name) and node.func.id == "isinstance" and len(node.args) == 2 \
                    and isinstance(node.args[0], ast.Name) and node.args[0].id == name:
                targets = node.args[1].elts if isinstance(node.args[1], ast.Tuple) else [node.args[1]]
                for t in targets:
                    q = self.qualified(t, fn)
                    if q in KEY_CLASS_TYPES:
                        alg, priv = KEY_CLASS_TYPES[q]
                        found.append(KeyType(algorithm=alg, private=priv, provenance=Provenance.PARAMETER, proximate=Provenance.PARAMETER,
                                             library="pycryptodome" if q.startswith(("Crypto.", "Cryptodome.")) else "pyca",
                                             origins=(Origin(node.lineno, node.col_offset, f"isinstance {q}"),)))
        if not found:
            return None
        return self._merge(found)

    # ------------------------------------------------------------------ attributes
    @staticmethod
    def _class_assigns_attr(cls: ast.ClassDef, attr: str) -> bool:
        for node in ast.walk(cls):
            if isinstance(node, ast.Assign):
                for t in node.targets:
                    if isinstance(t, ast.Attribute) and t.attr == attr and isinstance(t.value, ast.Name):
                        return True
                    if isinstance(t, ast.Name) and t.id == attr:
                        return True
        return False

    def _type_of_attribute(self, cls: ast.ClassDef, attr: str, fn: FunctionCtx | None, depth: int) -> AbstractType:
        """Union of every value assigned to `self.<attr>` anywhere in the class (and `attr = ...` in
        the class body). When the assigned value is a parameter of the method, the arguments passed
        at in-module call sites of that method (one level) are typed too; the external-caller path
        stays in the union as an Unknown with proximate PARAMETER."""
        key = ("attr", cls.name, attr)
        if key in self._cache:
            return self._cache[key]
        self._cache[key] = Unknown(reason="recursive")
        types: list[AbstractType] = []
        for sub in cls.body:
            if isinstance(sub, ast.Assign):
                for t in sub.targets:
                    if isinstance(t, ast.Name) and t.id == attr:
                        types.append(self.type_of_expr(sub.value, None, depth + 1))
            if isinstance(sub, (ast.FunctionDef, ast.AsyncFunctionDef)):
                mctx = self.functions.get(f"{cls.name}.{sub.name}")
                if not mctx or not mctx.self_name:
                    continue
                for node in ast.walk(sub):
                    if isinstance(node, ast.Assign):
                        for t in node.targets:
                            if isinstance(t, ast.Attribute) and isinstance(t.value, ast.Name) and t.value.id == mctx.self_name and t.attr == attr:
                                types.append(self.type_of_expr(node.value, mctx, depth + 1))
                                if isinstance(node.value, ast.Name) and self._is_parameter(node.value.id, mctx) and depth <= 3:
                                    types.extend(self._types_from_call_sites(cls, mctx, node.value.id, depth + 1))
                            elif isinstance(t, ast.Tuple):
                                # `self.a, self.b = vals`  /  `self.a, self.b = (x, y)`
                                for i, elt in enumerate(t.elts):
                                    if not (isinstance(elt, ast.Attribute) and isinstance(elt.value, ast.Name)
                                            and elt.value.id == mctx.self_name and elt.attr == attr):
                                        continue
                                    if isinstance(node.value, (ast.Tuple, ast.List)) and i < len(node.value.elts):
                                        types.append(self.type_of_expr(node.value.elts[i], mctx, depth + 1))
                                    elif isinstance(node.value, ast.Name) and self._is_parameter(node.value.id, mctx) and depth <= 3:
                                        types.append(Unknown(reason="untyped parameter", proximate=Provenance.PARAMETER))
                                        types.extend(self._types_from_call_sites(cls, mctx, node.value.id, depth + 1, index=i))
        # drop non-key noise (`self.key = None`, literals); keep real types and the parameter marker
        kept = [t for t in types if not (isinstance(t, Unknown) and t.proximate != Provenance.PARAMETER and t.reason != "pqc object")]
        if not kept and types:
            result: AbstractType = Unknown(reason="attribute without a typed assignment")
        elif not types:
            result = Unknown(reason="attribute never assigned in class")
        else:
            result = self._merge(kept)
        result.proximate = Provenance.ATTRIBUTE
        self._cache[key] = result
        return result

    def is_ctor_call(self, node: ast.Call, cls: ast.ClassDef) -> bool:
        """`Cls(...)`, or `self.__class__(...)` / `type(self)(...)` / `cls(...)` inside the class."""
        f = node.func
        if isinstance(f, ast.Name) and f.id == cls.name:
            return True
        inside = self.class_of_line(node.lineno) is cls
        if inside and isinstance(f, ast.Attribute) and f.attr == "__class__" and isinstance(f.value, ast.Name):
            return True
        if inside and isinstance(f, ast.Call) and isinstance(f.func, ast.Name) and f.func.id == "type":
            return True
        if inside and isinstance(f, ast.Name) and f.id == "cls":
            return True
        return False

    def _types_from_call_sites(self, cls: ast.ClassDef, method: FunctionCtx, param: str, depth: int,
                               index: int | None = None) -> list[AbstractType]:
        """Type the argument bound to `param` at every call of `method` in this module:
        constructor calls for `__init__`, `self.method(...)` inside the class otherwise.
        With `index`, the argument must be a tuple/list literal and its element `index` is typed."""
        params = [a.arg for a in method.node.args.args][1:]   # drop self
        kwonly = [a.arg for a in method.node.args.kwonlyargs]
        out: list[AbstractType] = []
        for node in ast.walk(self.tree):
            if not isinstance(node, ast.Call):
                continue
            is_ctor = method.name == "__init__" and self.is_ctor_call(node, cls)
            is_self_call = (method.name != "__init__" and isinstance(node.func, ast.Attribute) and node.func.attr == method.name
                            and isinstance(node.func.value, ast.Name) and self.class_of_line(node.lineno) is cls)
            if not (is_ctor or is_self_call):
                continue
            arg = None
            if param in params and params.index(param) < len(node.args):
                arg = node.args[params.index(param)]
            for kw in node.keywords:
                if kw.arg == param and (param in params or param in kwonly):
                    arg = kw.value
            if arg is None:
                continue
            if index is not None:
                if isinstance(arg, (ast.Tuple, ast.List)) and index < len(arg.elts):
                    arg = arg.elts[index]
                else:
                    continue
            caller = self.function_at(node.lineno)
            t = self.type_of_expr(arg, caller, depth + 1)
            if not isinstance(t, Unknown):
                t.via_call = (t.via_call or "") + f"|call-site:{node.lineno}"
                out.append(t)
        return out

    # ------------------------------------------------------------------ calls
    def _type_of_call(self, call: ast.Call, fn: FunctionCtx | None, depth: int) -> AbstractType:
        origin = Origin(call.lineno, call.col_offset, dotted(call.func) or "<call>")
        q = self.qualified(call.func, fn)
        if q:
            if q in PARAM_CONSTRUCTORS:
                kind, name = PARAM_CONSTRUCTORS[q]
                return ParamType(kind=kind, name=name, origins=(origin,))
            if q in KEY_FACTORIES:
                f = KEY_FACTORIES[q]
                kt = KeyType(library=f.library, algorithm=f.algorithm, private=f.private, provenance=f.provenance, origins=(origin,))
                self._fill_key_params(kt, call, fn, depth)
                return kt
            if q in CERT_LOADERS:
                return CertType(origins=(origin,))
            if q in NON_PK_OBJECTS or q.rsplit(".", 1)[0] in NON_PK_OBJECTS:
                return Unknown(reason="non-public-key object", origins=(origin,))
            for mod, scheme in SIGNER_MODULES.items():
                if q.endswith(mod + ".new") and q.startswith(("Crypto.", "Cryptodome.")):
                    key = self.type_of_expr(call.args[0], fn, depth + 1) if call.args else Unknown(reason="no key argument")
                    return SignerObject(scheme=scheme, key=key, origins=(origin,))
            for mod, scheme in CIPHER_MODULES.items():
                if q.endswith(mod + ".new") and q.startswith(("Crypto.", "Cryptodome.")):
                    key = self.type_of_expr(call.args[0], fn, depth + 1) if call.args else Unknown(reason="no key argument")
                    return CipherObject(scheme=scheme, key=key, origins=(origin,))
            if q.startswith(PQC_PREFIXES):
                return Unknown(reason="pqc object", origins=(origin,))
            if q in NUMBERS_CLASSES:
                return Unknown(reason="numbers object", origins=(origin,))
        # method calls on typed objects
        if isinstance(call.func, ast.Attribute):
            meth = call.func.attr
            base_expr = call.func.value
            # {...}.get(x) -> union of the dict's values
            if meth == "get" and isinstance(base_expr, ast.Dict):
                return self._merge([self.type_of_expr(v, fn, depth + 1) for v in base_expr.values if v is not None])
            # self.method(...) -> return type of that method (one level)
            if fn and fn.self_name and fn.cls is not None and isinstance(base_expr, ast.Name) and base_expr.id == fn.self_name:
                target = self.method_of(fn.cls, meth)
                if target and depth <= 2:
                    rets = [n.value for n in ast.walk(target.node) if isinstance(n, ast.Return) and n.value is not None]
                    if rets:
                        t = self._merge([self.type_of_expr(r, target, depth + 1) for r in rets])
                        t.via_call = target.qualname
                        return t
                    return Unknown(reason="method without return", via_call=target.qualname)
            # Numbers(...).private_key() / .public_key()
            if isinstance(base_expr, ast.Call):
                bq = self.qualified(base_expr.func, fn)
                if bq in NUMBERS_CLASSES and meth in ("private_key", "public_key"):
                    f = KEY_FACTORIES.get(f"{bq}.{meth}")
                    if f:
                        prov = Provenance.LOADED_JWK if self._looks_like_jwk(fn) else f.provenance
                        return KeyType(library=f.library, algorithm=f.algorithm, private=f.private, provenance=prov, origins=(origin,))
            base = self.type_of_expr(base_expr, fn, depth + 1)
            if isinstance(base, Unknown) and base.reason == "numbers object" and meth in ("private_key", "public_key"):
                # two-step: nums = RSAPrivateNumbers(...); key = nums.private_key()
                src = base.origins[0].text if base.origins else ""
                q2 = self.imports.resolve(src, fn.name if fn else None) if src else None
                f = KEY_FACTORIES.get(f"{q2}.{meth}") if q2 else None
                if f:
                    prov = Provenance.LOADED_JWK if self._looks_like_jwk(fn) else f.provenance
                    return KeyType(library=f.library, algorithm=f.algorithm, private=f.private, provenance=prov, origins=(origin,))
            if isinstance(base, Unknown) and base.reason == "pqc object" and meth in ("public_key", "publickey"):
                return Unknown(reason="pqc object", origins=base.origins + (origin,))
            if isinstance(base, KeyType):
                if meth in ("public_key", "publickey", "public_key_obj"):
                    return KeyType(library=base.library, algorithm=base.algorithm, private=False, provenance=base.provenance,
                                   key_size=base.key_size, curve=base.curve, origins=base.origins + (origin,), proximate=base.proximate)
                return Unknown(reason=f"method {meth} on key", origins=(origin,))
            if isinstance(base, CertType) and meth == "public_key":
                return KeyType(library="pyca", algorithm="ANY", private=False, provenance=Provenance.LOADED_CERTIFICATE, origins=base.origins + (origin,))
            if isinstance(base, Multi) and meth in ("public_key", "publickey"):
                opts = []
                for o in base.options:
                    if isinstance(o, KeyType):
                        opts.append(KeyType(library=o.library, algorithm=o.algorithm, private=False, provenance=o.provenance, origins=o.origins))
                    elif isinstance(o, CertType):
                        opts.append(KeyType(library="pyca", algorithm="ANY", private=False, provenance=Provenance.LOADED_CERTIFICATE, origins=o.origins))
                return self._merge(opts) if opts else Unknown(reason="public_key of unresolved")
        # one-level local function / class
        cls_here = fn.cls if fn else None
        if cls_here is not None and self.is_ctor_call(call, cls_here):
            return Instance(cls_name=cls_here.name, origins=(origin,))
        if isinstance(call.func, ast.Name):
            name = call.func.id
            if name in self.classes:
                return Instance(cls_name=name, origins=(origin,))
            if name in self.functions and depth == 0 or (name in self.functions and depth <= 2):
                target = self.functions[name]
                rets = [n.value for n in ast.walk(target.node) if isinstance(n, ast.Return) and n.value is not None]
                if rets:
                    types = [self.type_of_expr(r, target, depth + 1) for r in rets]
                    t = self._merge(types)
                    t.via_call = name
                    return t
                return Unknown(reason="local function without return", via_call=name)
        return Unknown(reason="unresolved callee", origins=(origin,))

    def _looks_like_jwk(self, fn: FunctionCtx | None) -> bool:
        if fn is None:
            return False
        names = {a.arg for a in fn.node.args.args} | {fn.name}
        return any("jwk" in n.lower() for n in names)

    def _fill_key_params(self, kt: KeyType, call: ast.Call, fn: FunctionCtx | None, depth: int = 0) -> None:
        for kw in call.keywords:
            if kw.arg in ("key_size", "bits") and isinstance(kw.value, ast.Constant) and isinstance(kw.value.value, int):
                kt.key_size = kw.value.value
            if kw.arg == "curve":
                kt.curve = self._curve_name(kw.value, fn, depth)
        for a in call.args:
            if isinstance(a, ast.Constant) and isinstance(a.value, int) and a.value >= 512:
                kt.key_size = a.value
            c = self._curve_name(a, fn, depth)
            if c:
                kt.curve = c

    def _curve_name(self, node: ast.AST, fn: FunctionCtx | None, depth: int = 0) -> str | None:
        target = node.func if isinstance(node, ast.Call) else node
        q = self.qualified(target, fn)
        if q and ".ec." in q:
            return q.rsplit(".", 1)[-1]
        if isinstance(node, ast.Constant) and isinstance(node.value, str) and node.value.upper().startswith(("P-", "NIST", "SECP", "ED", "CURVE")):
            return node.value
        if isinstance(node, (ast.Name, ast.Attribute)) and depth <= 4:
            # e.g. `self.curve` with a class attribute `curve = ec.SECP256R1()`
            t = self.type_of_expr(node, fn, depth + 1)
            names = {o.name for o in (t.options if isinstance(t, Multi) else (t,)) if isinstance(o, ParamType) and o.kind == "curve"}
            if len(names) == 1:
                return names.pop()
        return None

    # ------------------------------------------------------------------ merge
    @staticmethod
    def _merge(types: list[AbstractType]) -> AbstractType:
        flat: list[AbstractType] = []
        for t in types:
            if isinstance(t, Multi):
                flat.extend(t.options)
            else:
                flat.append(t)
        # an Unknown that came from a parameter is a real origin (an external caller), so it stays
        # in the union; other Unknowns (None, literals, unresolved helpers) are gaps and are dropped
        # once at least one typed option exists
        typed = [t for t in flat if not isinstance(t, Unknown)]
        param_marks = [t for t in flat if isinstance(t, Unknown) and t.proximate == Provenance.PARAMETER]
        unknown_reasons = [t.reason for t in flat if isinstance(t, Unknown)]
        if not typed:
            if param_marks:
                return param_marks[0]
            unknowns = [t for t in flat if isinstance(t, Unknown)]
            npk = [u for u in unknowns if u.reason == "non-public-key object"]
            if npk:
                return npk[0]
            # return the original object so its origins (e.g. a Numbers constructor) survive
            return unknowns[0] if unknowns else Unknown(reason="no assignments")
        meaningful = typed + param_marks[:1]
        # de-duplicate by description
        from .model import describe
        uniq: dict[str, AbstractType] = {}
        for t in meaningful:
            uniq.setdefault(describe(t), t)
        if len(uniq) == 1 and not unknown_reasons:
            return next(iter(uniq.values()))
        if len(uniq) == 1:
            # one real type plus some unresolved paths (e.g. `self.key = None`): keep the type, note the gap
            t = next(iter(uniq.values()))
            return t
        return Multi(options=tuple(uniq.values()))
