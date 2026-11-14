"""Module B — bounded Python semantic layer (ast-based; never imports or executes scanned code).

Scope-aware import/alias resolution, flow-insensitive def-use inside a function, class-wide
attribute typing, annotation / isinstance parameter typing, one-level resolution of calls to
functions and classes in the same module, argument resolution for operation calls, and bounded
consumer tracing for key material. Everything outside this scope is reported as Unknown with a
reason (explicit limitation), never guessed.
"""
