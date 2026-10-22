# -*- coding: utf-8 -*-
"""
ContactHub Enterprise v2.0 — Punto de Entrada Principal
=======================================================
Plataforma empresarial de gestión de contactos sobre registros de tamaño fijo (256 bytes)
con acceso aleatorio directo (seek/tell), índice primario JSON, verificación de integridad SHA-256
y entorno visual de alta fidelidad desarrollado en PySide6 y Qt Quick/QML.
"""

import os
import sys
import logging
from pathlib import Path

# Asegurar que el directorio raíz esté en sys.path y el CWD sea el del script
BASE_DIR = Path(__file__).resolve().parent
if str(BASE_DIR) not in sys.path:
    sys.path.insert(0, str(BASE_DIR))
os.chdir(str(BASE_DIR))

from config import (
    APP_NAME,
    APP_VERSION,
    APP_ORGANIZATION,
    LOG_FILE
)

# Configurar logging centralizado
logging.basicConfig(
    level=logging.INFO,
    format="[%(asctime)s] [%(levelname)s] (%(name)s) %(message)s",
    handlers=[
        logging.FileHandler(str(LOG_FILE), encoding="utf-8"),
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger("main")

from PySide6.QtWidgets import QApplication
from PySide6.QtQml import QQmlApplicationEngine
from PySide6.QtCore import QUrl
from PySide6.QtQuickControls2 import QQuickStyle

from src.viewmodels.app_controller import AppController


def main():
    logger.info("=" * 65)
    logger.info("Iniciando %s v%s", APP_NAME, APP_VERSION)
    logger.info("Organización: %s", APP_ORGANIZATION)
    logger.info("Python Runtime: %s", sys.version)
    logger.info("Directorio Base: %s", BASE_DIR)
    logger.info("=" * 65)

    # Forzar estilo 'Basic' para soporte óptimo de custom controls en QML
    QQuickStyle.setStyle("Basic")

    app = QApplication(sys.argv)
    app.setApplicationName(APP_NAME)
    app.setApplicationVersion(APP_VERSION)
    app.setOrganizationName(APP_ORGANIZATION)

    # Controlador central MVVM
    app_controller = AppController()

    # Motor de ejecución QML
    engine = QQmlApplicationEngine()

    ui_dir = BASE_DIR / "ui"
    engine.addImportPath(str(ui_dir))

    # Exponer controlador al contexto raíz de QML
    engine.rootContext().setContextProperty("appController", app_controller)

    # Cargar archivo principal de la interfaz
    qml_file = ui_dir / "main.qml"
    engine.load(QUrl.fromLocalFile(str(qml_file)))

    if not engine.rootObjects():
        logger.critical("Error fatal: No se pudo cargar la interfaz QML (%s). Abortando.", qml_file)
        sys.exit(-1)

    logger.info("Interfaz QML cargada exitosamente. Motor gráfico activo a 60 FPS.")
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
