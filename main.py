# -*- coding: utf-8 -*-
"""
ContactManager Pro — Sistema de Gestión de Contactos Empresarial.
Punto de entrada de la aplicación.

Laboratorio No. 2:
  - Archivo de registros de tamaño fijo (256 bytes)
  - Acceso aleatorio directo con seek() y tell()
  - Índice primario en JSON (indice.json)
  - Integridad criptográfica con hash SHA-256 (contactos.sha256)
  - Exportación a JSON y reporte PDF con fpdf2
  - Respaldos comprimidos ZIP con comparación de tamaño
  - Interfaz gráfica con efecto Liquid Glass y fondo animado
"""

import sys
import os
import logging

# Asegurar que el directorio raíz esté en sys.path
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
if BASE_DIR not in sys.path:
    sys.path.insert(0, BASE_DIR)

# Configurar directorio de logs
LOGS_DIR = os.path.join(BASE_DIR, 'logs')
os.makedirs(LOGS_DIR, exist_ok=True)
LOG_FILE = os.path.join(LOGS_DIR, 'app.log')

# Configurar logging central
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] (%(name)s) %(message)s',
    handlers=[
        logging.FileHandler(LOG_FILE, encoding='utf-8'),
        logging.StreamHandler(sys.stdout)
    ]
)

logger = logging.getLogger('main')


def main():
    """Iniciar la aplicación."""
    logger.info("=" * 60)
    logger.info("Iniciando ContactManager Pro — Edición Empresarial")
    logger.info("Python: %s", sys.version)
    logger.info("Directorio base: %s", BASE_DIR)
    logger.info("=" * 60)

    try:
        from ui.app import App
        app = App()
        app.mainloop()
    except Exception as exc:
        logger.critical("Error fatal al ejecutar la aplicación: %s", exc, exc_info=True)
        try:
            import tkinter.messagebox as mb
            mb.showerror("Error Fatal", f"No se pudo iniciar ContactManager Pro:\n\n{exc}")
        except Exception:
            pass
        sys.exit(1)


if __name__ == '__main__':
    main()
