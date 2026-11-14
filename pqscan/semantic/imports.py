"""Import and alias resolution for one module (scope-aware for top-level imports; local imports
inside functions are also collected, bound to the enclosing function)."""
from __future__ import annotations
import ast
from dataclasses import dataclass, field


@dataclass
class ImportMap:
    names: dict[str, str] = field(default_factory=dict)        # local name -> fully qualified name
    local: dict[str, dict[str, str]] = field(default_factory=dict)  # function qualname -> local imports

    @classmethod
    def from_module(cls, tree: ast.Module) -> "ImportMap":
        im = cls()
        im.names = im._collect(tree.body)
        for node in ast.walk(tree):
            if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
                loc = im._collect(node.body, recurse_into_defs=False)
                if loc:
                    im.local[node.name] = loc
        return im

    @staticmethod
    def _collect(stmts: list[ast.stmt], recurse_into_defs: bool = True) -> dict[str, str]:
        out: dict[str, str] = {}

        def visit(body: list[ast.stmt]) -> None:
            for s in body:
                if isinstance(s, ast.Import):
                    for a in s.names:
                        out[a.asname or a.name.split(".")[0]] = a.name if a.asname else a.name.split(".")[0]
                        if not a.asname and "." in a.name:
                            out[a.name] = a.name            # `import a.b.c` binds `a`; also allow full dotted use
                elif isinstance(s, ast.ImportFrom) and s.module and s.level == 0:
                    for a in s.names:
                        if a.name != "*":
                            out[a.asname or a.name] = f"{s.module}.{a.name}"
                elif isinstance(s, (ast.If, ast.Try, ast.With)):
                    for fld in ("body", "orelse", "finalbody", "handlers"):
                        for sub in getattr(s, fld, []) or []:
                            if isinstance(sub, ast.ExceptHandler):
                                visit(sub.body)
                            elif isinstance(sub, ast.stmt):
                                visit([sub])
                elif isinstance(s, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)) and recurse_into_defs:
                    pass  # local imports are collected per function separately
        visit(stmts)
        return out

    def resolve(self, dotted: str, function: str | None = None) -> str | None:
        """Resolve a dotted expression text (e.g. `R.generate_private_key`) to a fully qualified name,
        or None if its root is not an import binding."""
        parts = dotted.split(".")
        table = dict(self.names)
        if function and function in self.local:
            table.update(self.local[function])
        # longest-prefix match on dotted import bindings (`import a.b.c` style)
        for i in range(len(parts), 0, -1):
            head = ".".join(parts[:i])
            if head in table:
                base = table[head]
                tail = parts[i:]
                return ".".join([base] + tail) if tail else base
        return None
