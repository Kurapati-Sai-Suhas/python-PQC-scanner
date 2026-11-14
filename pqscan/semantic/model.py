"""Abstract value types produced by the typer. Every type records where it came from so that
Module C can cite evidence locations and Module F can score provenance edges."""
from __future__ import annotations
from dataclasses import dataclass, field
from ..models import Provenance


@dataclass(frozen=True)
class Origin:
    line: int
    col: int
    text: str = ""          # short description, e.g. "rsa.generate_private_key"


@dataclass
class AbstractType:
    origins: tuple[Origin, ...] = ()
    proximate: Provenance | None = None     # ATTRIBUTE / PARAMETER when read through one
    via_call: str | None = None            # local function name when typed through one call level


@dataclass
class KeyType(AbstractType):
    library: str = "pyca"
    algorithm: str = "ANY"                 # RSA | EC | X25519 | X448 | Ed25519 | Ed448 | DH | DSA | ANY
    private: bool | None = None            # None = unknown (e.g. PyCryptodome import_key)
    provenance: Provenance = Provenance.UNKNOWN
    key_size: int | None = None
    curve: str | None = None

    def family_single_purpose(self) -> str | None:
        """Algorithms whose role is fixed by the algorithm itself."""
        if self.algorithm in ("X25519", "X448", "DH"):
            return "KE"
        if self.algorithm in ("Ed25519", "Ed448", "DSA"):
            return "SIG"
        return None


@dataclass
class CertType(AbstractType):
    library: str = "pyca"
    provenance: Provenance = Provenance.LOADED_CERTIFICATE


@dataclass
class SignerObject(AbstractType):
    library: str = "pycryptodome"
    scheme: str = ""                       # pkcs1_15 | pss | DSS | eddsa | PKCS1_v1_5 | PKCS1_PSS
    key: AbstractType | None = None


@dataclass
class CipherObject(AbstractType):
    library: str = "pycryptodome"
    scheme: str = ""                       # PKCS1_OAEP | PKCS1_v1_5
    key: AbstractType | None = None


@dataclass
class ParamType(AbstractType):
    """A parameter object: padding / hash / signature-algorithm wrapper / curve."""
    kind: str = ""        # padding | hash | sigalg | kex | curve | mgf
    name: str = ""        # PKCS1v15 | PSS | OAEP | SHA256 | ECDSA | ECDH | SECP256R1 ...


@dataclass
class Multi(AbstractType):
    """Several possible types (e.g. an attribute assigned in two methods)."""
    options: tuple[AbstractType, ...] = ()


@dataclass
class Instance(AbstractType):
    """An instance of a class defined in the scanned module (not a key)."""
    cls_name: str = ""


@dataclass
class Unknown(AbstractType):
    reason: str = "unresolved"


def describe(t: AbstractType | None) -> str:
    if t is None:
        return "none"
    if isinstance(t, KeyType):
        p = {True: "private", False: "public", None: "key"}[t.private]
        return f"{t.library}:{t.algorithm}:{p}:{t.provenance.value}"
    if isinstance(t, CertType):
        return "pyca:certificate"
    if isinstance(t, SignerObject):
        return f"pcd:signer:{t.scheme}({describe(t.key)})"
    if isinstance(t, CipherObject):
        return f"pcd:cipher:{t.scheme}({describe(t.key)})"
    if isinstance(t, Instance):
        return f"instance:{t.cls_name}"
    if isinstance(t, ParamType):
        return f"param:{t.kind}:{t.name}"
    if isinstance(t, Multi):
        return "multi{" + "|".join(sorted(describe(o) for o in t.options)) + "}"
    return f"unknown({t.reason})"
