"""
Módulo de almacenamiento y persistencia de ContactHub Enterprise.
Implementa el motor binario de bajo nivel con registros fijos de 256 bytes,
índice primario JSON y verificación de sellos criptográficos SHA-256.
"""

from .record_manager import (
    RecordManager,
    pack_field,
    unpack_field,
    pack_record,
    unpack_record
)
from .index_manager import IndexManager
from .integrity_manager import IntegrityManager

__all__ = [
    "RecordManager",
    "pack_field",
    "unpack_field",
    "pack_record",
    "unpack_record",
    "IndexManager",
    "IntegrityManager"
]
