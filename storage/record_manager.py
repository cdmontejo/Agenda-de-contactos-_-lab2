"""
Gestor de registros de tamaño fijo para la Agenda de Contactos.

Cada registro ocupa exactamente 256 bytes en el archivo binario.
Los campos se codifican en UTF-8 y se rellenan con espacios (0x20)
hasta alcanzar el tamaño exacto en bytes especificado.

Funciones de empaquetado/desempaquetado:
  - pack_field:   codifica un campo a bytes con relleno
  - unpack_field: decodifica bytes a cadena limpia
  - pack_record:  empaqueta un diccionario de contacto en 256 bytes
  - unpack_record: desempaqueta 256 bytes en un diccionario

Clase RecordManager:
  Gestiona lectura, escritura y actualización de registros usando
  seek() y tell() para acceso directo por posición.
"""

import os
import logging
from datetime import datetime

import sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from config import (
    RECORD_SIZE, FIELDS_SPEC, FIELD_NEWLINE_SIZE, FIELD_PADDING_SIZE
)

logger = logging.getLogger(__name__)


# ═══════════════════════════════════════════════════════════
# Funciones de empaquetado / desempaquetado de campos
# ═══════════════════════════════════════════════════════════

def pack_field(value: str, size: int) -> bytes:
    """
    Codifica una cadena a UTF-8 y la ajusta a exactamente *size* bytes.

    Si la cadena codificada excede *size*, se truncan caracteres desde
    el final uno a uno hasta que quepa, evitando cortar secuencias
    multibyte.  El resultado se rellena con espacios (0x20) por la
    derecha hasta completar *size* bytes.

    Args:
        value: Cadena de texto a empaquetar.
        size:  Tamaño objetivo en bytes.

    Returns:
        Objeto ``bytes`` de exactamente *size* bytes.
    """
    text = str(value) if value is not None else ""
    encoded = text.encode('utf-8')

    # Truncar carácter a carácter si excede el tamaño
    if len(encoded) > size:
        chars = list(text)
        while chars:
            encoded = ''.join(chars).encode('utf-8')
            if len(encoded) <= size:
                break
            chars.pop()
        else:
            encoded = b''

    # Rellenar con espacios hasta el tamaño exacto
    return encoded.ljust(size, b' ')


def unpack_field(data: bytes) -> str:
    """
    Decodifica bytes UTF-8 y elimina espacios de relleno al final.

    Args:
        data: Bytes a decodificar.

    Returns:
        Cadena limpia sin relleno.
    """
    try:
        return data.decode('utf-8').rstrip()
    except UnicodeDecodeError:
        logger.warning("Error al decodificar campo, usando latin-1 como respaldo")
        return data.decode('latin-1').rstrip()


def pack_record(contact: dict) -> bytes:
    """
    Empaqueta un diccionario de contacto en exactamente RECORD_SIZE bytes.

    El diccionario debe contener las claves: id, nombre, telefono,
    correo, ciudad.  La clave 'estado' es opcional (por defecto 'A').
    Se añade relleno (padding) y un salto de línea al final.

    Args:
        contact: Diccionario con los datos del contacto.

    Returns:
        Objeto ``bytes`` de exactamente 256 bytes.

    Raises:
        AssertionError: Si el registro resultante no tiene 256 bytes.
    """
    # Asegurar que el estado tenga un valor por defecto
    estado = contact.get('estado', 'A')

    record = b''
    for field_name, field_size in FIELDS_SPEC:
        if field_name == '_padding':
            record += b' ' * field_size
        elif field_name == 'estado':
            record += pack_field(estado, field_size)
        else:
            record += pack_field(contact.get(field_name, ''), field_size)

    # Añadir salto de línea
    record += b'\n'

    assert len(record) == RECORD_SIZE, (
        f"El registro debe tener {RECORD_SIZE} bytes, "
        f"pero tiene {len(record)} bytes"
    )

    return record


def unpack_record(data: bytes) -> dict | None:
    """
    Desempaqueta RECORD_SIZE bytes en un diccionario de contacto.

    Args:
        data: Bytes a desempaquetar (debe tener RECORD_SIZE bytes).

    Returns:
        Diccionario con las claves id, nombre, telefono, correo,
        ciudad, estado; o ``None`` si los datos son inválidos.
    """
    if data is None or len(data) != RECORD_SIZE:
        logger.warning(
            "Datos de registro inválidos: se esperaban %d bytes, "
            "se recibieron %d",
            RECORD_SIZE,
            len(data) if data else 0
        )
        return None

    try:
        result = {}
        offset = 0

        for field_name, field_size in FIELDS_SPEC:
            chunk = data[offset:offset + field_size]
            if field_name != '_padding':
                result[field_name] = unpack_field(chunk)
            offset += field_size

        # Ignorar el byte de salto de línea (ya se procesó como padding + \n)
        return result

    except Exception as exc:
        logger.error("Error al desempaquetar registro: %s", exc)
        return None


# ═══════════════════════════════════════════════════════════
# Clase RecordManager
# ═══════════════════════════════════════════════════════════

class RecordManager:
    """
    Gestiona el archivo de registros de tamaño fijo.

    Cada registro ocupa exactamente RECORD_SIZE (256) bytes.
    Se utiliza seek() para acceso directo y tell() para reportar
    la posición actual del cursor en el archivo.
    """

    def __init__(self, filepath: str):
        """
        Inicializa el gestor de registros.

        Si el archivo no existe, se crea vacío.

        Args:
            filepath: Ruta completa al archivo de datos.
        """
        self.filepath = filepath

        # Crear el archivo si no existe
        try:
            if not os.path.exists(filepath):
                directory = os.path.dirname(filepath)
                if directory:
                    os.makedirs(directory, exist_ok=True)
                with open(filepath, 'wb') as f:
                    pass  # Crear archivo vacío
                logger.info("Archivo de datos creado: %s", filepath)
            else:
                logger.info("Archivo de datos existente: %s", filepath)
        except (OSError, PermissionError) as exc:
            logger.error(
                "No se pudo crear/verificar el archivo %s: %s",
                filepath, exc
            )

    def add_record(self, contact: dict) -> int:
        """
        Añade un nuevo registro al final del archivo.

        Posiciona el cursor al final con seek(), empaqueta el
        contacto y escribe exactamente RECORD_SIZE bytes.

        Args:
            contact: Diccionario con los datos del contacto.

        Returns:
            Número de registro (0-based) del registro añadido.
        """
        record_data = pack_record(contact)

        try:
            with open(self.filepath, 'ab') as f:
                # Posicionar al final del archivo
                f.seek(0, 2)  # SEEK_END
                position = f.tell()
                record_num = position // RECORD_SIZE

                logger.info(
                    "Añadiendo registro #%d en posición %d (tell=%d)",
                    record_num, position, position
                )

                f.write(record_data)
                final_position = f.tell()

                logger.info(
                    "Registro #%d escrito. Posición final: tell=%d",
                    record_num, final_position
                )

            return record_num

        except (OSError, PermissionError) as exc:
            logger.error("Error al añadir registro: %s", exc)
            raise

    def read_record(self, record_num: int) -> dict | None:
        """
        Lee un registro por su número usando acceso directo.

        Calcula la posición como record_num * RECORD_SIZE y usa
        seek() para posicionarse directamente.

        Args:
            record_num: Número del registro (0-based).

        Returns:
            Diccionario con los datos del contacto, o ``None`` si
            el registro no existe o hay error.
        """
        try:
            with open(self.filepath, 'rb') as f:
                # Calcular posición y hacer seek
                position = record_num * RECORD_SIZE
                f.seek(position)

                logger.info(
                    "Leyendo registro #%d: seek(%d), tell=%d",
                    record_num, position, f.tell()
                )

                data = f.read(RECORD_SIZE)

                final_position = f.tell()
                logger.info(
                    "Registro #%d leído. Posición final: tell=%d, "
                    "bytes leídos=%d",
                    record_num, final_position, len(data)
                )

                if len(data) != RECORD_SIZE:
                    logger.warning(
                        "Registro #%d incompleto: %d bytes de %d esperados",
                        record_num, len(data), RECORD_SIZE
                    )
                    return None

                return unpack_record(data)

        except FileNotFoundError:
            logger.error("Archivo no encontrado: %s", self.filepath)
            return None
        except (OSError, PermissionError) as exc:
            logger.error(
                "Error al leer registro #%d: %s", record_num, exc
            )
            return None

    def update_record(self, record_num: int, contact: dict):
        """
        Actualiza un registro existente en su posición exacta.

        Sobrescribe únicamente los RECORD_SIZE bytes del registro
        indicado, sin afectar registros vecinos.

        Args:
            record_num: Número del registro a actualizar (0-based).
            contact:    Diccionario con los nuevos datos del contacto.
        """
        record_data = pack_record(contact)

        try:
            with open(self.filepath, 'r+b') as f:
                # Calcular posición y hacer seek
                position = record_num * RECORD_SIZE
                f.seek(position)

                logger.info(
                    "Actualizando registro #%d: seek(%d), tell=%d",
                    record_num, position, f.tell()
                )

                f.write(record_data)
                f.flush()

                final_position = f.tell()
                logger.info(
                    "Registro #%d actualizado. Posición final: tell=%d",
                    record_num, final_position
                )

        except FileNotFoundError:
            logger.error("Archivo no encontrado: %s", self.filepath)
            raise
        except (OSError, PermissionError) as exc:
            logger.error(
                "Error al actualizar registro #%d: %s", record_num, exc
            )
            raise

    def get_total_records(self) -> int:
        """
        Calcula el número total de registros en el archivo.

        Returns:
            Número total de registros (tamaño del archivo / RECORD_SIZE).
        """
        try:
            file_size = os.path.getsize(self.filepath)
            total = file_size // RECORD_SIZE
            logger.debug(
                "Total de registros: %d (tamaño archivo: %d bytes)",
                total, file_size
            )
            return total
        except FileNotFoundError:
            logger.warning("Archivo no encontrado: %s", self.filepath)
            return 0
        except OSError as exc:
            logger.error("Error al obtener tamaño del archivo: %s", exc)
            return 0

    def read_all_records(self) -> list[dict]:
        """
        Lee todos los registros del archivo secuencialmente.

        Returns:
            Lista de diccionarios con los datos de cada contacto.
            Los registros inválidos se omiten.
        """
        records = []

        try:
            total = self.get_total_records()
            if total == 0:
                return records

            with open(self.filepath, 'rb') as f:
                for i in range(total):
                    data = f.read(RECORD_SIZE)
                    if len(data) != RECORD_SIZE:
                        logger.warning(
                            "Registro #%d truncado, se detiene la lectura", i
                        )
                        break
                    contact = unpack_record(data)
                    if contact is not None:
                        records.append(contact)

            logger.info("Se leyeron %d registros del archivo", len(records))

        except FileNotFoundError:
            logger.warning("Archivo no encontrado: %s", self.filepath)
        except (OSError, PermissionError) as exc:
            logger.error("Error al leer todos los registros: %s", exc)

        return records

    def get_file_info(self) -> dict:
        """
        Obtiene información detallada sobre el archivo de datos.

        Returns:
            Diccionario con las claves:
              - size:          tamaño en bytes
              - modified:      fecha de modificación (ISO 8601)
              - readable:      si el archivo es legible
              - writable:      si el archivo es escribible
              - total_records: número total de registros
              - path:          ruta completa al archivo
        """
        info = {
            'size': 0,
            'modified': '',
            'readable': False,
            'writable': False,
            'total_records': 0,
            'path': self.filepath,
        }

        try:
            if os.path.exists(self.filepath):
                stat = os.stat(self.filepath)
                info['size'] = stat.st_size
                info['modified'] = datetime.fromtimestamp(
                    stat.st_mtime
                ).isoformat()
                info['readable'] = os.access(self.filepath, os.R_OK)
                info['writable'] = os.access(self.filepath, os.W_OK)
                info['total_records'] = stat.st_size // RECORD_SIZE
            else:
                logger.warning(
                    "Archivo no encontrado para info: %s", self.filepath
                )

        except OSError as exc:
            logger.error("Error al obtener info del archivo: %s", exc)

        return info
