"""
Validadores de entrada para la Agenda de Contactos.

Cada función de validación retorna una tupla (bool, str):
  - (True,  "")             si el valor es válido
  - (False, "mensaje error") si el valor es inválido

La función validate_contact() valida todos los campos de un
diccionario de contacto de forma conjunta.
"""

import logging

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from config import (
    FIELD_NOMBRE_SIZE, FIELD_TELEFONO_SIZE,
    FIELD_CORREO_SIZE, FIELD_CIUDAD_SIZE
)

logger = logging.getLogger(__name__)


def check_field_fits(value: str, max_bytes: int) -> bool:
    """
    Verifica si una cadena codificada en UTF-8 cabe en max_bytes.

    Args:
        value:     Cadena a verificar.
        max_bytes: Máximo de bytes permitidos.

    Returns:
        ``True`` si la cadena codificada cabe, ``False`` si no.
    """
    try:
        return len(value.encode('utf-8')) <= max_bytes
    except (AttributeError, UnicodeEncodeError):
        return False


def validate_id(value) -> tuple[bool, str]:
    """
    Valida que el ID sea un entero positivo.

    Args:
        value: Valor a validar (puede ser str, int, etc.).

    Returns:
        Tupla (válido, mensaje_error).
    """
    try:
        id_int = int(value)
        if id_int <= 0:
            return (False, "El ID debe ser un número positivo mayor que 0")
        return (True, "")
    except (ValueError, TypeError):
        return (False, "El ID debe ser un número entero válido")


def validate_name(value: str) -> tuple[bool, str]:
    """
    Valida el nombre del contacto.

    Reglas:
      - No puede estar vacío
      - Máximo 70 caracteres (para caber en 80 bytes con UTF-8)
      - No puede ser solo números

    Args:
        value: Nombre a validar.

    Returns:
        Tupla (válido, mensaje_error).
    """
    if not value or not str(value).strip():
        return (False, "El nombre no puede estar vacío")

    name = str(value).strip()

    if len(name) > 70:
        return (False, "El nombre no puede exceder 70 caracteres")

    if name.isdigit():
        return (False, "El nombre no puede ser solo números")

    if not check_field_fits(name, FIELD_NOMBRE_SIZE):
        return (
            False,
            f"El nombre excede el límite de {FIELD_NOMBRE_SIZE} bytes en UTF-8"
        )

    return (True, "")


def validate_phone(value: str) -> tuple[bool, str]:
    """
    Valida el número de teléfono.

    Reglas:
      - No puede estar vacío
      - Solo permite dígitos, +, -, (, ), espacios
      - Al menos 7 dígitos

    Args:
        value: Teléfono a validar.

    Returns:
        Tupla (válido, mensaje_error).
    """
    if not value or not str(value).strip():
        return (False, "El teléfono no puede estar vacío")

    phone = str(value).strip()

    # Verificar caracteres permitidos
    allowed = set('0123456789+-() ')
    for char in phone:
        if char not in allowed:
            return (
                False,
                f"Carácter no permitido en teléfono: '{char}'. "
                f"Solo se permiten dígitos, +, -, (, ), y espacios"
            )

    # Contar dígitos
    digit_count = sum(1 for c in phone if c.isdigit())
    if digit_count < 7:
        return (
            False,
            f"El teléfono debe tener al menos 7 dígitos "
            f"(se encontraron {digit_count})"
        )

    if not check_field_fits(phone, FIELD_TELEFONO_SIZE):
        return (
            False,
            f"El teléfono excede el límite de {FIELD_TELEFONO_SIZE} bytes"
        )

    return (True, "")


def validate_email(value: str) -> tuple[bool, str]:
    """
    Valida el correo electrónico con verificación básica.

    Reglas:
      - No puede estar vacío
      - Debe contener exactamente un @
      - Debe tener un punto después del @
      - No puede comenzar ni terminar con @
      - La parte del dominio debe tener al menos 2 caracteres después
        del último punto

    Args:
        value: Correo a validar.

    Returns:
        Tupla (válido, mensaje_error).
    """
    if not value or not str(value).strip():
        return (False, "El correo electrónico no puede estar vacío")

    email = str(value).strip()

    # Verificar @
    if '@' not in email:
        return (False, "El correo debe contener '@'")

    at_count = email.count('@')
    if at_count != 1:
        return (False, "El correo debe contener exactamente un '@'")

    local_part, domain_part = email.split('@')

    if not local_part:
        return (False, "Falta la parte local del correo (antes de '@')")

    if not domain_part:
        return (False, "Falta el dominio del correo (después de '@')")

    # Verificar punto en dominio
    if '.' not in domain_part:
        return (False, "El dominio debe contener al menos un punto")

    # Verificar extensión mínima
    parts = domain_part.rsplit('.', 1)
    if len(parts) < 2 or len(parts[1]) < 2:
        return (
            False,
            "La extensión del dominio debe tener al menos 2 caracteres"
        )

    if not check_field_fits(email, FIELD_CORREO_SIZE):
        return (
            False,
            f"El correo excede el límite de {FIELD_CORREO_SIZE} bytes"
        )

    return (True, "")


def validate_city(value: str) -> tuple[bool, str]:
    """
    Valida la ciudad del contacto.

    Reglas:
      - No puede estar vacía
      - Máximo 45 caracteres

    Args:
        value: Ciudad a validar.

    Returns:
        Tupla (válido, mensaje_error).
    """
    if not value or not str(value).strip():
        return (False, "La ciudad no puede estar vacía")

    city = str(value).strip()

    if len(city) > 45:
        return (False, "La ciudad no puede exceder 45 caracteres")

    if not check_field_fits(city, FIELD_CIUDAD_SIZE):
        return (
            False,
            f"La ciudad excede el límite de {FIELD_CIUDAD_SIZE} bytes en UTF-8"
        )

    return (True, "")


def validate_contact(data: dict) -> tuple[bool, list[str]]:
    """
    Valida todos los campos de un diccionario de contacto.

    Ejecuta cada validador individual y recopila todos los errores.

    Args:
        data: Diccionario con las claves id, nombre, telefono,
              correo, ciudad.

    Returns:
        Tupla (todo_válido, lista_de_errores):
          - (True,  [])         si todos los campos son válidos
          - (False, [errores])  si hay al menos un campo inválido
    """
    errors = []

    # Validar ID
    valid, msg = validate_id(data.get('id', ''))
    if not valid:
        errors.append(f"ID: {msg}")

    # Validar nombre
    valid, msg = validate_name(data.get('nombre', ''))
    if not valid:
        errors.append(f"Nombre: {msg}")

    # Validar teléfono
    valid, msg = validate_phone(data.get('telefono', ''))
    if not valid:
        errors.append(f"Teléfono: {msg}")

    # Validar correo
    valid, msg = validate_email(data.get('correo', ''))
    if not valid:
        errors.append(f"Correo: {msg}")

    # Validar ciudad
    valid, msg = validate_city(data.get('ciudad', ''))
    if not valid:
        errors.append(f"Ciudad: {msg}")

    if errors:
        logger.debug("Validación fallida: %d errores", len(errors))
        return (False, errors)

    return (True, [])
