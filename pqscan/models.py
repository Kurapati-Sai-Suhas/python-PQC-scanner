"""Core data types shared by all modules. Pure data; no behaviour that touches the file system."""
from __future__ import annotations
from dataclasses import dataclass, field, asdict
from enum import Enum
from typing import Any


class Library(str, Enum):
    PYCA = "pyca"
    PYCRYPTODOME = "pycryptodome"
    UNKNOWN = "unknown"


class CandidateKind(str, Enum):
    KEYGEN = "keygen"              # creates key material in process
    LOADER = "loader"              # parses key material from PEM/DER/SSH/certificate
    CONSTRUCT = "construct"        # rebuilds key material from numbers / scalar / encoded point
    OPERATION = "operation"        # a call whose API fixes the operation (e.g. pkcs1_15.new(k).sign)
    SIGNER_OBJECT = "signer-object"    # PyCryptodome Signature.*.new(key)
    CIPHER_OBJECT = "cipher-object"    # PyCryptodome Cipher.PKCS1_*.new(key)
    METHOD_CANDIDATE = "method-candidate"  # $recv.sign/verify/exchange/encrypt/decrypt — receiver untyped
    PQC_PRESENCE = "pqc-presence"  # ML-KEM / ML-DSA / liboqs usage (hybrid evidence)
    PARAMETERS = "parameters"      # dh.generate_parameters etc.


class Role(str, Enum):
    SIGN = "SIGN"
    VERIFY = "VERIFY"
    KEY_ESTABLISHMENT = "KEY_ESTABLISHMENT"
    PK_ENCRYPT = "PK_ENCRYPT"
    PK_DECRYPT = "PK_DECRYPT"
    KEY_MATERIAL_ONLY = "KEY_MATERIAL_ONLY"
    PROTOCOL_CONFIG = "PROTOCOL_CONFIG"
    UNKNOWN = "UNKNOWN"


class Tier(str, Enum):
    T0 = "T0"
    T1 = "T1"
    T2 = "T2"
    T3 = "T3"

    @property
    def rank(self) -> int:
        return int(self.value[1])


class Provenance(str, Enum):
    GENERATED = "generated"
    LOADED_PEM = "loaded-PEM"
    LOADED_DER = "loaded-DER"
    LOADED_SSH = "loaded-SSH"
    LOADED_JWK = "loaded-JWK"
    LOADED_CERTIFICATE = "loaded-certificate"
    CONSTRUCTED = "constructed-from-parsed-blob"
    PARAMETER = "parameter"
    ATTRIBUTE = "attribute"
    ENV_OR_KMS = "env-or-KMS"
    UNKNOWN = "unknown"


@dataclass(frozen=True)
class Location:
    file: str          # path relative to the scan root, POSIX separators
    line: int          # 1-based
    col: int           # 1-based
    end_line: int
    end_col: int


@dataclass
class Candidate:
    """A Semgrep candidate (Module A output)."""
    location: Location
    rule_id: str
    library: Library
    kind: CandidateKind
    algorithm: str                     # RSA, EC, X25519, X448, Ed25519, Ed448, DH, DSA, ML-KEM, ML-DSA, ANY
    api: str                           # fully qualified API as named in api_coverage.md
    coverage_row: str                  # C1..C24, D1..D12, or "-"
    snippet: str = ""                  # the source line, truncated (<= 200 chars), never key bytes
    extra: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        d = asdict(self)
        d["library"] = self.library.value
        d["kind"] = self.kind.value
        return d
