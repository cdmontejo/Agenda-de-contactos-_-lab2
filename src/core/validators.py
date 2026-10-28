"""
Validadores de entrada y límites en bytes para ContactHub Enterprise.
Garantiza que ningún campo sobrepase los límites de tamaño estricto del registro fijo.
"""

import re
from typing import Tuple, List, Dict, Any
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent))
from config import (
    FIELD_NOMBRE_SIZE,
    FIELD_TELEFONO_SIZE,
    FIELD_CORREO_SIZE,
    FIELD_CIUDAD_SIZE
)

EMAIL_REGEX = re.compile(r"^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$")
PHONE_REGEX = re.compile(r"^[\+]?[0-9\s\-\(\)\.]{4,20}$")


def check_field_fits(value: str, max_bytes: int) -> bool:
    """Verifica si la cadena codificada en UTF-8 no supera el límite de bytes."""
    try:
        return len(str(value).encode("utf-8")) <= max_bytes
    except Exception:
        return False


def validate_id(value: Any) -> Tuple[bool, str]:
    """Valida que el ID sea un entero positivo mayor que cero."""
    try:
        val_int = int(str(value).strip())
        if val_int <= 0:
            return False, "El ID debe ser un número entero positivo mayor a 0."
        if val_int > 9_999_999_999:
            return False, "El ID excede el límite máximo de 10 dígitos."
        return True, ""
    except (ValueError, TypeError):
        return False, "El ID debe ser un número entero válido."


def validate_nombre(value: Any) -> Tuple[bool, str]:
    """Valida que el nombre no esté vacío y no supere 80 bytes UTF-8."""
    text = str(value or "").strip()
    if not text:
        return False, "El nombre del contacto es obligatorio."
    if not check_field_fits(text, FIELD_NOMBRE_SIZE):
        return False, f"El nombre excede el límite de {FIELD_NOMBRE_SIZE} bytes en UTF-8."
    return True, ""


def validate_telefono(value: Any) -> Tuple[bool, str]:
    """Valida el formato telefónico y longitud máxima de 20 bytes."""
    text = str(value or "").strip()
    if not text:
        return False, "El número de teléfono es obligatorio."
    if not check_field_fits(text, FIELD_TELEFONO_SIZE):
        return False, f"El teléfono excede los {FIELD_TELEFONO_SIZE} bytes permitidos."
    if not PHONE_REGEX.match(text):
        return False, "El teléfono contiene caracteres inválidos (use dígitos, +, -, espacios o paréntesis)."
    return True, ""


def validate_correo(value: Any) -> Tuple[bool, str]:
    """Valida el formato de correo electrónico y límite de 80 bytes."""
    text = str(value or "").strip()
    if not text:
        return False, "El correo electrónico es obligatorio."
    if not check_field_fits(text, FIELD_CORREO_SIZE):
        return False, f"El correo excede los {FIELD_CORREO_SIZE} bytes permitidos."
    if not EMAIL_REGEX.match(text):
        return False, "El correo electrónico no tiene un formato válido (ejemplo@dominio.com)."
    return True, ""


def validate_ciudad(value: Any) -> Tuple[bool, str]:
    """Valida que la ciudad no esté vacía y no supere 50 bytes."""
    text = str(value or "").strip()
    if not text:
        return False, "La ciudad es obligatoria."
    if not check_field_fits(text, FIELD_CIUDAD_SIZE):
        return False, f"La ciudad excede los {FIELD_CIUDAD_SIZE} bytes permitidos."
    return True, ""


def validate_contact(data: Dict[str, Any]) -> Tuple[bool, List[str]]:
    """
    Valida exhaustivamente todos los campos requeridos de un contacto.
    Retorna una tupla (es_valido, lista_de_errores).
    """
    errors: List[str] = []

    ok, msg = validate_id(data.get("id"))
    if not ok:
        errors.append(msg)

    ok, msg = validate_nombre(data.get("nombre"))
    if not ok:
        errors.append(msg)

    ok, msg = validate_telefono(data.get("telefono"))
    if not ok:
        errors.append(msg)

    ok, msg = validate_correo(data.get("correo"))
    if not ok:
        errors.append(msg)

    ok, msg = validate_ciudad(data.get("ciudad"))
    if not ok:
        errors.append(msg)

    return len(errors) == 0, errors

