"""
Configuración central de la Agenda de Contactos Empresarial.
Define constantes de registros, rutas de archivos y metadatos.

ESTRUCTURA DEL REGISTRO (256 bytes totales):
  - id:       10 bytes  (entero único, alineado a la derecha)
  - nombre:   80 bytes  (nombre completo, soporta UTF-8/acentos)
  - telefono: 20 bytes  (número de teléfono)
  - correo:   80 bytes  (correo electrónico)
  - ciudad:   50 bytes  (ciudad)
  - estado:    1 byte   (A=Activo, D=Eliminado)
  - padding:  14 bytes  (relleno con espacios)
  - newline:   1 byte   (\\n para legibilidad del archivo)
  TOTAL:     256 bytes por registro

Todas las longitudes son en BYTES, no caracteres.
Los campos se codifican en UTF-8 y se rellenan con espacios (0x20).
"""
import os

# ── Metadatos de la aplicación ─────────────────────────────
APP_NAME = "ContactManager Pro"
APP_VERSION = "1.0.0"
APP_SUBTITLE = "Sistema de Gestión de Contactos Empresarial"

# ── Estructura del registro (tamaños en BYTES) ────────────
FIELD_ID_SIZE = 10
FIELD_NOMBRE_SIZE = 80
FIELD_TELEFONO_SIZE = 20
FIELD_CORREO_SIZE = 80
FIELD_CIUDAD_SIZE = 50
FIELD_ESTADO_SIZE = 1
FIELD_PADDING_SIZE = 14
FIELD_NEWLINE_SIZE = 1

RECORD_SIZE = (FIELD_ID_SIZE + FIELD_NOMBRE_SIZE + FIELD_TELEFONO_SIZE +
               FIELD_CORREO_SIZE + FIELD_CIUDAD_SIZE + FIELD_ESTADO_SIZE +
               FIELD_PADDING_SIZE + FIELD_NEWLINE_SIZE)  # = 256

# Verificar que el tamaño del registro sea exactamente 256 bytes
assert RECORD_SIZE == 256, (
    f"RECORD_SIZE debe ser 256 bytes, pero se calculó {RECORD_SIZE}"
)

# Campos en orden para empaquetado/desempaquetado
FIELDS_SPEC = [
    ('id', FIELD_ID_SIZE),
    ('nombre', FIELD_NOMBRE_SIZE),
    ('telefono', FIELD_TELEFONO_SIZE),
    ('correo', FIELD_CORREO_SIZE),
    ('ciudad', FIELD_CIUDAD_SIZE),
    ('estado', FIELD_ESTADO_SIZE),
    ('_padding', FIELD_PADDING_SIZE),
]

# ── Rutas de archivos ─────────────────────────────────────
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.join(BASE_DIR, 'data')
EXPORTS_DIR = os.path.join(BASE_DIR, 'exports')
BACKUPS_DIR = os.path.join(BASE_DIR, 'backups')
LOGS_DIR = os.path.join(BASE_DIR, 'logs')

CONTACTS_FILE = os.path.join(DATA_DIR, 'contactos.dat')
INDEX_FILE = os.path.join(DATA_DIR, 'indice.json')
HASH_FILE = os.path.join(DATA_DIR, 'contactos.sha256')

# ── Crear directorios necesarios ──────────────────────────
for _d in [DATA_DIR, EXPORTS_DIR, BACKUPS_DIR, LOGS_DIR]:
    os.makedirs(_d, exist_ok=True)
