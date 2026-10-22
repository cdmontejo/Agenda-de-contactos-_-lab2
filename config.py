"""
Configuración central de ContactHub Enterprise.
Define constantes de registros de tamaño fijo (256 bytes), rutas de archivos y metadatos.

ESTRUCTURA DEL REGISTRO BINARIO (256 bytes totales):
  - id:       10 bytes  (entero único, justificado a la derecha con espacios)
  - nombre:   80 bytes  (nombre completo en UTF-8, soporta acentos, diéresis y ñ)
  - telefono: 20 bytes  (número telefónico con formato)
  - correo:   80 bytes  (correo electrónico)
  - ciudad:   50 bytes  (ciudad de residencia)
  - estado:    1 byte   ('A'=Activo, 'D'=Eliminado lógicamente)
  - padding:  14 bytes  (relleno con espacios 0x20 para alineación)
  - newline:   1 byte   (\\n = 0x0A para legibilidad en inspección hexadecimal)
  TOTAL:     256 bytes estrictos por registro

Todas las longitudes se miden en BYTES estrictos (no caracteres).
El acceso aleatorio directo se calcula como: offset = record_num * 256
"""

import os
from pathlib import Path

# ── Metadatos de la aplicación ────────────────────────────────────────────────
APP_NAME = "ContactHub Enterprise"
APP_VERSION = "2.0.0"
APP_SUBTITLE = "Plataforma Empresarial de Gestión de Contactos con Acceso Aleatorio"
APP_ORGANIZATION = "URL Ingeniería - Lab No. 2"

# ── Especificación de Registros Binarios de Tamaño Fijo ────────────────────────
FIELD_ID_SIZE = 10
FIELD_NOMBRE_SIZE = 80
FIELD_TELEFONO_SIZE = 20
FIELD_CORREO_SIZE = 80
FIELD_CIUDAD_SIZE = 50
FIELD_ESTADO_SIZE = 1
FIELD_PADDING_SIZE = 14
FIELD_NEWLINE_SIZE = 1

RECORD_SIZE = (
    FIELD_ID_SIZE +
    FIELD_NOMBRE_SIZE +
    FIELD_TELEFONO_SIZE +
    FIELD_CORREO_SIZE +
    FIELD_CIUDAD_SIZE +
    FIELD_ESTADO_SIZE +
    FIELD_PADDING_SIZE +
    FIELD_NEWLINE_SIZE
)

# Validación matemática estricta: debe ser exactamente 256 bytes
assert RECORD_SIZE == 256, f"RECORD_SIZE debe ser exactamente 256 bytes, se calculó {RECORD_SIZE}"

# Especificación secuencial de campos para empaquetado/desempaquetado
FIELDS_SPEC = [
    ('id', FIELD_ID_SIZE),
    ('nombre', FIELD_NOMBRE_SIZE),
    ('telefono', FIELD_TELEFONO_SIZE),
    ('correo', FIELD_CORREO_SIZE),
    ('ciudad', FIELD_CIUDAD_SIZE),
    ('estado', FIELD_ESTADO_SIZE),
    ('_padding', FIELD_PADDING_SIZE),
]

# ── Directorios del Sistema ───────────────────────────────────────────────────
BASE_DIR = Path(__file__).resolve().parent
DATA_DIR = BASE_DIR / "data"
EXPORTS_DIR = BASE_DIR / "exports"
BACKUPS_DIR = BASE_DIR / "backups"
LOGS_DIR = BASE_DIR / "logs"
ASSETS_DIR = BASE_DIR / "ui" / "assets"

# Rutas de persistencia primaria
CONTACTS_FILE = DATA_DIR / "contactos.dat"
INDEX_FILE = DATA_DIR / "indice.json"
HASH_FILE = DATA_DIR / "contactos.sha256"
SETTINGS_FILE = DATA_DIR / "settings.json"
LOG_FILE = LOGS_DIR / "app.log"

# Asegurar existencia de carpetas críticas
for folder in [DATA_DIR, EXPORTS_DIR, BACKUPS_DIR, LOGS_DIR, ASSETS_DIR]:
    folder.mkdir(parents=True, exist_ok=True)
