"""
Gestor de registros de tamaño fijo para ContactHub Enterprise.
Implementa acceso aleatorio directo en disco mediante seek() y tell() sobre
registros inmutables de 256 bytes en contactos.dat.
"""

import os
import logging
from pathlib import Path
from typing import Dict, Any, List, Optional, Tuple

import sys
sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent))
from config import (
    RECORD_SIZE,
    FIELDS_SPEC,
    FIELD_ID_SIZE,
    FIELD_NOMBRE_SIZE,
    FIELD_TELEFONO_SIZE,
    FIELD_CORREO_SIZE,
    FIELD_CIUDAD_SIZE,
    FIELD_ESTADO_SIZE,
    FIELD_PADDING_SIZE,
    FIELD_NEWLINE_SIZE
)

logger = logging.getLogger("storage.record_manager")


def pack_field(value: Any, size: int) -> bytes:
    """
    Codifica un valor a bytes UTF-8 y lo ajusta con precisión a exactamente *size* bytes.
    Si la representación en bytes UTF-8 sobrepasa *size*, elimina caracteres del final
    uno a uno hasta que quepa, evitando romper secuencias multibyte (tildes, eñes, diéresis).
    Finalmente rellena a la derecha con espacios (0x20) hasta alcanzar el tamaño exacto.
    """
    text = str(value) if value is not None else ""
    encoded = text.encode("utf-8")

    if len(encoded) > size:
        chars = list(text)
        while chars:
            encoded = "".join(chars).encode("utf-8")
            if len(encoded) <= size:
                break
            chars.pop()
        else:
            encoded = b""

    # Relleno con espacios a la derecha hasta completar 'size' bytes
    return encoded.ljust(size, b" ")


def unpack_field(data: bytes) -> str:
    """
    Decodifica bytes UTF-8 y elimina espacios de relleno a la derecha.
    Si encuentra una secuencia corrupta, recurre a latin-1 para salvaguardar la lectura.
    """
    try:
        return data.decode("utf-8").rstrip(" ")
    except UnicodeDecodeError:
        logger.warning("Decodificación UTF-8 falló en campo binario; aplicando fallback latin-1.")
        return data.decode("latin-1").rstrip(" ")


def pack_record(contact: Dict[str, Any]) -> bytes:
    """
    Empaqueta un diccionario de contacto en exactamente 256 bytes estandarizados.
    Formato:
      id (10B), nombre (80B), telefono (20B), correo (80B), ciudad (50B),
      estado (1B), padding (14B), newline (1B = \\n)
    """
    estado = str(contact.get("estado", "A"))[:1] or "A"
    
    # El ID se alinea a la derecha para consistencia numérica en visualización
    raw_id = str(contact.get("id", "")).strip()
    id_bytes = raw_id.encode("utf-8")
    if len(id_bytes) > FIELD_ID_SIZE:
        id_bytes = id_bytes[:FIELD_ID_SIZE]
    id_packed = id_bytes.rjust(FIELD_ID_SIZE, b" ")

    record = bytearray()
    record.extend(id_packed)
    record.extend(pack_field(contact.get("nombre", ""), FIELD_NOMBRE_SIZE))
    record.extend(pack_field(contact.get("telefono", ""), FIELD_TELEFONO_SIZE))
    record.extend(pack_field(contact.get("correo", ""), FIELD_CORREO_SIZE))
    record.extend(pack_field(contact.get("ciudad", ""), FIELD_CIUDAD_SIZE))
    record.extend(estado.encode("ascii")[:1].ljust(FIELD_ESTADO_SIZE, b"A"))
    record.extend(b" " * FIELD_PADDING_SIZE)
    record.extend(b"\n")

    assert len(record) == RECORD_SIZE, (
        f"El registro generado tiene {len(record)} bytes, se requieren exactamente {RECORD_SIZE}."
    )
    return bytes(record)


def unpack_record(data: bytes) -> Optional[Dict[str, Any]]:
    """
    Desempaqueta un bloque de exactamente 256 bytes en un diccionario estructurado.
    Retorna None si la longitud no es exactamente RECORD_SIZE.
    """
    if not data or len(data) != RECORD_SIZE:
        logger.warning("Intento de desempaquetar bloque inválido de %d bytes (esperados: %d)",
                       len(data) if data else 0, RECORD_SIZE)
        return None

    try:
        offset = 0
        
        # ID (10 bytes)
        id_raw = data[offset:offset + FIELD_ID_SIZE]
        id_val = unpack_field(id_raw).strip()
        offset += FIELD_ID_SIZE

        # Nombre (80 bytes)
        nombre = unpack_field(data[offset:offset + FIELD_NOMBRE_SIZE])
        offset += FIELD_NOMBRE_SIZE

        # Teléfono (20 bytes)
        telefono = unpack_field(data[offset:offset + FIELD_TELEFONO_SIZE])
        offset += FIELD_TELEFONO_SIZE

        # Correo (80 bytes)
        correo = unpack_field(data[offset:offset + FIELD_CORREO_SIZE])
        offset += FIELD_CORREO_SIZE

        # Ciudad (50 bytes)
        ciudad = unpack_field(data[offset:offset + FIELD_CIUDAD_SIZE])
        offset += FIELD_CIUDAD_SIZE

        # Estado (1 byte: 'A' o 'D')
        estado = data[offset:offset + FIELD_ESTADO_SIZE].decode("ascii", errors="replace")
        offset += FIELD_ESTADO_SIZE

        return {
            "id": int(id_val) if id_val.isdigit() else id_val,
            "nombre": nombre,
            "telefono": telefono,
            "correo": correo,
            "ciudad": ciudad,
            "estado": estado
        }
    except Exception as exc:
        logger.error("Error al desempaquetar registro binario: %s", exc)
        return None


class RecordManager:
    """
    Controlador de acceso directo aleatorio y persistencia física para contactos.dat.
    Garantiza lectura y modificación in-place en disco sin desplazar registros vecinos.
    """

    def __init__(self, filepath: Path | str):
        self.filepath = Path(filepath)
        self._ensure_file_exists()

    def _ensure_file_exists(self) -> None:
        """Crea el archivo binario vacío si aún no existe en el sistema de archivos."""
        try:
            self.filepath.parent.mkdir(parents=True, exist_ok=True)
            if not self.filepath.exists():
                with open(self.filepath, "wb") as f:
                    pass
                logger.info("Archivo de datos inicializado: %s", self.filepath)
        except Exception as exc:
            logger.error("No se pudo inicializar el archivo de datos %s: %s", self.filepath, exc)

    def add_record(self, contact: Dict[str, Any]) -> Tuple[int, int, int]:
        """
        Añade un nuevo registro al final del archivo.
        Usa seek(0, os.SEEK_END) y tell() para calcular el número de registro físico.
        
        Returns:
            Tuple[record_num, offset_inicial, offset_final]
        """
        record_bytes = pack_record(contact)
        with open(self.filepath, "ab") as f:
            f.seek(0, os.SEEK_END)
            pos_inicial = f.tell()
            record_num = pos_inicial // RECORD_SIZE

            f.write(record_bytes)
            f.flush()
            pos_final = f.tell()

        logger.debug("Registro #%d añadido en offset %d (tell=%d)", record_num, pos_inicial, pos_final)
        return record_num, pos_inicial, pos_final

    def read_record(self, record_num: int) -> Tuple[Optional[Dict[str, Any]], int, int]:
        """
        Lee un registro por su posición ordinal mediante acceso directo aleatorio O(1).
        
        Calcula offset = record_num * 256 y realiza f.seek(offset).
        
        Returns:
            Tuple[contact_dict, tell_antes, tell_despues]
        """
        target_offset = record_num * RECORD_SIZE
        with open(self.filepath, "rb") as f:
            f.seek(target_offset, os.SEEK_SET)
            tell_antes = f.tell()
            data = f.read(RECORD_SIZE)
            tell_despues = f.tell()

        if len(data) != RECORD_SIZE:
            logger.warning("Lectura en record #%d incompleta (%d bytes leídos)", record_num, len(data))
            return None, tell_antes, tell_despues

        contact = unpack_record(data)
        return contact, tell_antes, tell_despues

    def update_record(self, record_num: int, contact: Dict[str, Any]) -> Tuple[int, int]:
        """
        Modifica un registro existente in-place directamente en su posición binaria.
        Abre en modo 'r+b', hace seek(record_num * 256) y sobrescribe exactamente 256 bytes.
        No altera registros precedentes ni posteriores.
        
        Returns:
            Tuple[tell_antes, tell_despues]
        """
        record_bytes = pack_record(contact)
        target_offset = record_num * RECORD_SIZE

        with open(self.filepath, "r+b") as f:
            f.seek(target_offset, os.SEEK_SET)
            tell_antes = f.tell()
            f.write(record_bytes)
            f.flush()
            tell_despues = f.tell()

        logger.debug("Registro #%d actualizado in-place en offset %d", record_num, target_offset)
        return tell_antes, tell_despues

    def read_raw_bytes(self, record_num: int) -> bytes:
        """Lee los 256 bytes crudos de un registro para el inspector hexadecimal."""
        target_offset = record_num * RECORD_SIZE
        with open(self.filepath, "rb") as f:
            f.seek(target_offset, os.SEEK_SET)
            return f.read(RECORD_SIZE)

    def get_total_records(self) -> int:
        """Calcula el número de registros dividiendo el tamaño del archivo entre 256."""
        if not self.filepath.exists():
            return 0
        file_size = self.filepath.stat().st_size
        return file_size // RECORD_SIZE

    def read_all_records(self, include_deleted: bool = False) -> List[Tuple[int, Dict[str, Any]]]:
        """
        Escanea secuencialmente todos los registros del archivo binario.
        Retorna lista de tuplas: (record_num, contact_dict)
        """
        results = []
        total = self.get_total_records()

        with open(self.filepath, "rb") as f:
            for rec_num in range(total):
                f.seek(rec_num * RECORD_SIZE, os.SEEK_SET)
                chunk = f.read(RECORD_SIZE)
                if len(chunk) == RECORD_SIZE:
                    contact = unpack_record(chunk)
                    if contact:
                        if include_deleted or contact.get("estado") == "A":
                            results.append((rec_num, contact))
        return results

    def tamper_byte(self, record_num: int, relative_offset: int, bad_byte: int = 0xFF) -> bool:
        """
        Inyecta deliberadamente un byte corrupto en un registro para demostraciones
        didácticas de rotura del sello criptográfico SHA-256.
        """
        target_offset = (record_num * RECORD_SIZE) + (relative_offset % RECORD_SIZE)
        with open(self.filepath, "r+b") as f:
            f.seek(target_offset, os.SEEK_SET)
            f.write(bytes([bad_byte]))
            f.flush()
        logger.warning("Demostración didáctica: Byte alterado en offset %d", target_offset)
        return True

    def clear(self) -> None:
        """Vacía el archivo de datos (útil para pruebas o reinicios controlados)."""
        with open(self.filepath, "wb") as f:
            pass
        logger.info("Archivo de datos vaciado: %s", self.filepath)
