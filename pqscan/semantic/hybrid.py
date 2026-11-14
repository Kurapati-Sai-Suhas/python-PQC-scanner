"""Evidence that a classical operation is combined with an approved PQ counterpart (PQ/T hybrid).

Design rule: a false "no action needed" is false assurance, while a missed hybrid only costs a
migration note. The check is therefore deliberately conservative. A classical site counts as part of
an approved hybrid only when, inside ONE function (nested functions and lambdas ignored):

key establishment
  * the classical shared secret is bound directly to a name (`a = k.exchange(peer)`), or returned by a
    helper whose result is bound directly to a name at an in-module call site (one level);
  * an ML-KEM shared secret is bound directly to a name: `ss = R.decapsulate(ct)`, `ss, ct = R.encapsulate()`
    (first element only; never the ciphertext) or `ss = R.encapsulate()[0]`, where R is typed as an ML-KEM
    object or is an untyped parameter (never a local class instance or a classical key);
signatures
  * the classical signature and an ML-DSA signature (receiver typed as an ML-DSA object) are bound
    directly to names and both sign the same message expression;
and for both:
  * each of the two names is assigned exactly once in the function, the names differ, and their two
    defining statements sit in the same statement block (so if/else, try/except and loop alternatives
    never count);
  * a later statement of that block combines both names directly as operands of a concatenation (`+`),
    an f-string, a `join` of a list/tuple, or a call whose callee name looks like a combiner/KDF/hash.
    Bare tuples, comparisons and arbitrary calls (logging, storage) do not count.
verification
  * the classical verify and an ML-DSA verify are both unconditional expression statements in the same
    block (not alternatives, not an exception fallback) and verify the same message expression.
Downgrade guards (confirmation review, 14 Nov 2026):
  * after its definition, the classical name may be read only inside the accepted combiner or in a
    validation check (comparison, `bytes_eq`, `compare_digest`, `len`); any other use (a classical-only
    KDF, an early `return hash(a)`, a debug-only branch) means the classical secret is used on its own;
  * the combining statement is a top-level statement of the definitions' block, and no `return` lies
    between the definitions and it (a `raise` aborts, so it is allowed);
  * a helper's return is followed only for a private helper (leading underscore) and only if EVERY
    in-module call site combines;
  * an untyped KEM parameter is rejected if any in-module caller passes a non-ML-KEM object;
  * signing: the message name is not reassigned in the function;
  * verification: no `return` between the two verifies, and no enclosing `try` whose handler does not
    re-raise (a swallowed PQ failure is not a hybrid check).
This shows data combination, not that the combiner meets SP 800-227 Sec. 4.6.
"""
from __future__ import annotations
import ast
import re
from .model import Multi, Unknown, Instance, KeyType
from .typer import ModuleTyper, FunctionCtx

KEM_METHODS = {"encapsulate", "decapsulate"}
COMBINER_NAME = re.compile(r"(kdf|hkdf|derive|combin|hash|sha|blake|hmac|xwing|concat)", re.I)
VALIDATION_CALL = re.compile(r"^(bytes_eq|compare_digest|len|isinstance)$")
NESTED = (ast.FunctionDef, ast.AsyncFunctionDef, ast.Lambda, ast.ClassDef)


# ------------------------------------------------------------------ AST helpers (nested scopes excluded)
def _walk(root: ast.AST):
    stack = list(ast.iter_child_nodes(root))
    while stack:
        n = stack.pop()
        yield n
        if isinstance(n, NESTED):
            continue
        stack.extend(ast.iter_child_nodes(n))


def _parents(root: ast.AST) -> dict[int, ast.AST]:
    out: dict[int, ast.AST] = {}
    stack = [root]
    while stack:
        n = stack.pop()
        for c in ast.iter_child_nodes(n):
            out[id(c)] = n
            if not isinstance(c, NESTED):
                stack.append(c)
    return out


def _block(stmt: ast.stmt, parents: dict[int, ast.AST]) -> tuple[int, int] | None:
    """(id of the statement list containing `stmt`, index in it)."""
    p = parents.get(id(stmt))
    if p is None:
        return None
    for field in ("body", "orelse", "finalbody"):
        lst = getattr(p, field, None)
        if isinstance(lst, list):
            for i, s in enumerate(lst):
                if s is stmt:
                    return (id(lst), i)
    return None


def _stmt_of(node: ast.AST, parents: dict[int, ast.AST]) -> ast.stmt | None:
    while node is not None and not isinstance(node, ast.stmt):
        node = parents.get(id(node))
    return node


def _top_in_block(node: ast.AST, block_id: int, parents: dict[int, ast.AST]) -> int | None:
    """Index, in the block `block_id`, of the statement that contains `node`."""
    stmt = _stmt_of(node, parents)
    while stmt is not None:
        b = _block(stmt, parents)
        if b and b[0] == block_id:
            return b[1]
        stmt = _stmt_of(parents.get(id(stmt)), parents)
    return None


def _store_count(fn_node: ast.AST, name: str) -> int:
    return sum(1 for n in _walk(fn_node) if isinstance(n, ast.Name) and n.id == name and isinstance(n.ctx, ast.Store))


def _same_expr(a: ast.AST | None, b: ast.AST | None) -> bool:
    return a is not None and b is not None and ast.dump(a) == ast.dump(b)


# ------------------------------------------------------------------ typing of PQ receivers
def _pq_kind(typer: ModuleTyper, recv: ast.AST, fn: FunctionCtx) -> str | None:
    """'mlkem' / 'mldsa' when typed as that PQ object, 'param' for an untyped parameter, else None."""
    t = typer.type_of_expr(recv, fn)
    opts = t.options if isinstance(t, Multi) else (t,)
    kinds = set()
    for o in opts:
        if isinstance(o, Unknown) and o.reason == "pqc object":
            text = " ".join(og.text.lower() for og in o.origins)
            kinds.add("mlkem" if "mlkem" in text else "mldsa" if "mldsa" in text else "other-pq")
        elif isinstance(o, Unknown) and o.reason == "untyped parameter":
            kinds.add("param")
        elif isinstance(o, (Instance, KeyType)):
            return None                      # a local class or a classical key is never an ML-KEM/ML-DSA object
        else:
            kinds.add("unknown")
    for k in ("mlkem", "mldsa"):
        if kinds == {k}:
            return k
    if kinds == {"param"}:
        if isinstance(recv, ast.Name) and _param_fed_non_pq(typer, fn, recv.id):
            return None
        return "param"
    return None


def _param_fed_non_pq(typer: ModuleTyper, fn: FunctionCtx, param: str) -> bool:
    """True if an in-module call of `fn` passes a local class instance or a classical key as `param`."""
    params = [a.arg for a in fn.node.args.args]
    if fn.cls is not None and fn.self_name:
        params = params[1:]
    for c in _call_sites(typer, fn):
        arg = None
        if param in params and params.index(param) < len(c.args):
            arg = c.args[params.index(param)]
        for kw in c.keywords:
            if kw.arg == param:
                arg = kw.value
        if arg is None:
            continue
        t = typer.type_of_expr(arg, typer.function_at(c.lineno))
        opts = t.options if isinstance(t, Multi) else (t,)
        if any(isinstance(o, (Instance, KeyType)) for o in opts):
            return True
    return False


# ------------------------------------------------------------------ value bindings
def _direct_binding(stmt: ast.stmt, call: ast.Call) -> str | None:
    """Name bound directly to `call` (or to its first tuple element) by `stmt`."""
    if not isinstance(stmt, ast.Assign) or len(stmt.targets) != 1:
        return None
    t, v = stmt.targets[0], stmt.value
    if v is call and isinstance(t, ast.Name):
        return t.id
    if v is call and isinstance(t, ast.Tuple) and t.elts and isinstance(t.elts[0], ast.Name):
        return t.elts[0].id
    if (isinstance(v, ast.Subscript) and v.value is call and isinstance(v.slice, ast.Constant) and v.slice.value == 0
            and isinstance(t, ast.Name)):
        return t.id
    return None


def _pq_secrets(typer: ModuleTyper, fn: FunctionCtx, operation: str, parents) -> list[tuple[str, ast.stmt, ast.Call]]:
    out = []
    for n in _walk(fn.node):
        if not (isinstance(n, ast.Call) and isinstance(n.func, ast.Attribute)):
            continue
        stmt = _stmt_of(n, parents)
        if operation == "exchange" and n.func.attr in KEM_METHODS:
            if _pq_kind(typer, n.func.value, fn) not in ("mlkem", "param"):
                continue
            name = _direct_binding(stmt, n)
            if name is None:
                continue
            # `ss, ct = R.encapsulate()` binds the secret first; `x = R.encapsulate()` binds the whole pair
            if n.func.attr == "encapsulate" and isinstance(stmt.value, ast.Call) and isinstance(stmt.targets[0], ast.Name):
                continue
            out.append((name, stmt, n))
        elif operation == "sign" and n.func.attr == "sign" and _pq_kind(typer, n.func.value, fn) == "mldsa":
            name = _direct_binding(stmt, n)
            if name is not None:
                out.append((name, stmt, n))
    return out


def _combined(node: ast.AST, a: str, b: str) -> bool:
    """`node` combines the names a and b directly in an accepted combining form."""
    def leaves(e: ast.AST) -> list[ast.AST]:
        if isinstance(e, ast.BinOp) and isinstance(e.op, ast.Add):
            return leaves(e.left) + leaves(e.right)
        return [e]
    def names(es) -> set[str]:
        return {e.id for e in es if isinstance(e, ast.Name)}
    if isinstance(node, ast.BinOp) and isinstance(node.op, ast.Add):
        return {a, b} <= names(leaves(node))
    if isinstance(node, ast.JoinedStr):
        return {a, b} <= names(v.value for v in node.values if isinstance(v, ast.FormattedValue))
    if isinstance(node, ast.Call) and isinstance(node.func, ast.Attribute) and node.func.attr == "join" and node.args \
            and isinstance(node.args[0], (ast.List, ast.Tuple)):
        return {a, b} <= names(node.args[0].elts)
    if isinstance(node, ast.Call):
        callee = node.func.attr if isinstance(node.func, ast.Attribute) else (node.func.id if isinstance(node.func, ast.Name) else "")
        return bool(COMBINER_NAME.search(callee)) and {a, b} <= names(list(node.args) + [k.value for k in node.keywords])
    return False


def _pair_combined(fn: FunctionCtx, parents, a: str, a_stmt: ast.stmt, b: str, b_stmt: ast.stmt) -> bool:
    if a == b or _store_count(fn.node, a) != 1 or _store_count(fn.node, b) != 1:
        return False
    ba, bb = _block(a_stmt, parents), _block(b_stmt, parents)
    if ba is None or bb is None or ba[0] != bb[0]:
        return False                         # alternatives (if/else, try/except, loop bodies) never count
    after = max(ba[1], bb[1])
    block_list = _block_list(a_stmt, parents)
    for n in _walk(fn.node):
        if not _combined(n, a, b):
            continue
        st = _stmt_of(n, parents)
        sb = _block(st, parents) if st is not None else None
        if sb is None or sb[0] != ba[0] or sb[1] < after:
            continue                         # the combiner must be a top-level statement of the same block
        between = block_list[after + 1:sb[1]]
        if any(isinstance(x, ast.Return) for s in between for x in [s, *_walk(s)]):
            continue                         # an early return before the combination is a downgrade path
        if not _sole_sink(fn, parents, a, a_stmt, n):
            continue                         # the classical secret is also used on its own
        return True
    return False


def _block_list(stmt: ast.stmt, parents) -> list[ast.stmt]:
    p = parents.get(id(stmt))
    for field in ("body", "orelse", "finalbody"):
        lst = getattr(p, field, None)
        if isinstance(lst, list) and any(s is stmt for s in lst):
            return lst
    return []


def _sole_sink(fn: FunctionCtx, parents, name: str, def_stmt: ast.stmt, combiner: ast.AST, allow_return: bool = False) -> bool:
    """Every read of `name` lies inside `combiner` or in a validation check (or, for a helper, is its return)."""
    inside = {id(x) for x in ast.walk(combiner)}
    for n in _walk(fn.node):
        if not (isinstance(n, ast.Name) and n.id == name and isinstance(n.ctx, ast.Load)):
            continue
        if id(n) in inside:
            continue
        if _in_validation(n, parents):
            continue
        if allow_return and isinstance(parents.get(id(n)), ast.Return):
            continue
        return False
    return True


def _in_validation(node: ast.AST, parents) -> bool:
    p = parents.get(id(node))
    while p is not None and not isinstance(p, ast.stmt):
        if isinstance(p, ast.Compare):
            return True
        if isinstance(p, ast.Call):
            f = p.func
            nm = f.attr if isinstance(f, ast.Attribute) else (f.id if isinstance(f, ast.Name) else "")
            return bool(VALIDATION_CALL.match(nm))
        p = parents.get(id(p))
    return False


def _call_sites(typer: ModuleTyper, fn: FunctionCtx) -> list[ast.Call]:
    out = []
    for node in ast.walk(typer.tree):
        if not isinstance(node, ast.Call):
            continue
        f = node.func
        if fn.cls is None and isinstance(f, ast.Name) and f.id == fn.name:
            out.append(node)
        elif fn.cls is not None and isinstance(f, ast.Attribute) and f.attr == fn.name and typer.class_of_line(node.lineno) is fn.cls:
            out.append(node)
    return out


# ------------------------------------------------------------------ entry point
def combined_hybrid(typer: ModuleTyper, op_call: ast.Call, fn: FunctionCtx | None, operation: str) -> bool:
    if fn is None or operation not in ("exchange", "sign", "verify"):
        return False
    parents = _parents(fn.node)
    op_stmt = _stmt_of(op_call, parents)

    if operation == "verify":
        if not (isinstance(op_stmt, ast.Expr) and op_stmt.value is op_call):
            return False
        ob = _block(op_stmt, parents)
        data = op_call.args[1] if len(op_call.args) > 1 else None
        for n in _walk(fn.node):
            if (n is not op_call and isinstance(n, ast.Call) and isinstance(n.func, ast.Attribute) and n.func.attr == "verify"
                    and _pq_kind(typer, n.func.value, fn) == "mldsa"):
                st = _stmt_of(n, parents)
                sb = _block(st, parents) if st is not None else None
                if not (isinstance(st, ast.Expr) and st.value is n and ob is not None and sb is not None and sb[0] == ob[0]
                        and _same_expr(data, n.args[1] if len(n.args) > 1 else None)):
                    continue
                lst = _block_list(op_stmt, parents)
                lo, hi = sorted((ob[1], sb[1]))
                if any(isinstance(x, ast.Return) for s in lst[lo + 1:hi] for x in [s, *_walk(s)]):
                    continue                 # verification of the second scheme can be skipped
                if _in_swallowing_try(op_stmt, parents):
                    continue                 # a failure of either verification is swallowed
                if isinstance(data, ast.Name) and _store_count(fn.node, data.id) > 0 and fn.node.args and \
                        any(a.arg == data.id for a in fn.node.args.args):
                    continue                 # message rebound inside the function
                return True
        return False

    # classical value: (function, name, defining statement)
    scopes: list[tuple[FunctionCtx, str, ast.stmt]] = []
    name = _direct_binding(op_stmt, op_call) if op_stmt is not None else None
    if name is not None:
        scopes.append((fn, name, op_stmt))
        returns = [n for n in _walk(fn.node) if isinstance(n, ast.Return) and n.value is not None]
        if returns and all(isinstance(r.value, ast.Name) and r.value.id == name for r in returns) and _store_count(fn.node, name) == 1:
            scopes += _caller_scopes(typer, fn)
    elif isinstance(op_stmt, ast.Return) and op_stmt.value is op_call:
        scopes += _caller_scopes(typer, fn)
    msg = op_call.args[0] if operation == "sign" and op_call.args else None
    if operation == "sign" and isinstance(msg, ast.Name) and _store_count(fn.node, msg.id) > (0 if _is_param(fn, msg.id) else 1):
        return False                         # the message is rebound: the two signatures may cover different data

    def combined_in(f, cname, cstmt) -> bool:
        fparents = _parents(f.node)
        for pname, pstmt, pcall in _pq_secrets(typer, f, operation, fparents):
            if operation == "sign" and not _same_expr(msg, pcall.args[0] if pcall.args else None):
                continue
            if _pair_combined(f, fparents, cname, cstmt, pname, pstmt):
                return True
        return False

    own = [s for s in scopes if s[0] is fn]
    callers = [s for s in scopes if s[0] is not fn]
    if any(combined_in(*s) for s in own):
        return True
    # through a helper: private, every in-module call site combines, and inside the helper the secret
    # is only validated and returned
    if callers and fn.name.startswith("_") and all(combined_in(*s) for s in callers):
        if name is None:
            return len(callers) == len(_call_sites(typer, fn))
        if _sole_sink(fn, parents, name, op_stmt, ast.Pass(), allow_return=True):
            return len(callers) == len(_call_sites(typer, fn))
    return False


def _is_param(fn: FunctionCtx, name: str) -> bool:
    a = fn.node.args
    return any(p.arg == name for p in a.posonlyargs + a.args + a.kwonlyargs)


def _in_swallowing_try(stmt: ast.stmt, parents) -> bool:
    """`stmt` is inside a try body whose handlers do not all re-raise."""
    node = stmt
    p = parents.get(id(node))
    while p is not None:
        if isinstance(p, ast.Try) and any(s is node for s in p.body):
            for h in p.handlers:
                if not any(isinstance(x, ast.Raise) for x in ast.walk(h)):
                    return True
        node, p = p, parents.get(id(p))
    return False


def _caller_scopes(typer: ModuleTyper, fn: FunctionCtx) -> list[tuple[FunctionCtx, str, ast.stmt]]:
    out = []
    for c in _call_sites(typer, fn):
        caller = typer.function_at(c.lineno)
        if caller is None:
            continue
        cp = _parents(caller.node)
        st = _stmt_of(c, cp)
        nm = _direct_binding(st, c) if st is not None else None
        if nm is not None:
            out.append((caller, nm, st))
    return out
