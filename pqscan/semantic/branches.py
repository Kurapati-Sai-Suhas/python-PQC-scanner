"""Mutually exclusive branches (if/else, try/except) for bounded flow-sensitivity."""
from __future__ import annotations
import ast


def _stmt_containing(root: ast.AST, target: ast.AST) -> ast.stmt | None:
    best = None
    for node in ast.walk(root):
        if isinstance(node, ast.stmt) and node is not root and any(n is target for n in ast.walk(node)):
            if best is None or node.lineno >= best.lineno:
                best = node
    return best


def _branch_path(root: ast.AST, target: ast.AST) -> list[tuple[int, str]] | None:
    """Sequence of (id(compound statement), branch field) from root down to target."""
    def visit(node, path):
        if node is target:
            return path
        for field in ("body", "orelse", "finalbody", "handlers"):
            for child in getattr(node, field, None) or []:
                r = visit(child, path + [(id(node), field)] if isinstance(node, (ast.If, ast.Try, ast.IfExp)) or
                          type(node).__name__ == "TryStar" else path)
                if r is not None:
                    return r
        for child in ast.iter_child_nodes(node):
            if child is target or any(c is target for c in ast.walk(child)):
                if not isinstance(child, ast.stmt) and not isinstance(child, ast.ExceptHandler):
                    return path
        return None
    return visit(root, [])


def exclusive_branches(root: ast.AST, a: ast.AST, b: ast.AST) -> bool:
    """True when a and b sit in different branches of the same if/else or try/except."""
    pa, pb = _branch_path(root, _stmt_containing(root, a) or a), _branch_path(root, b)
    if pa is None or pb is None:
        return False
    for (na, fa), (nb, fb) in zip(pa, pb):
        if na != nb:
            return False
        if fa != fb:
            return {fa, fb} != {"body", "finalbody"} and "finalbody" not in (fa, fb)
    return False


