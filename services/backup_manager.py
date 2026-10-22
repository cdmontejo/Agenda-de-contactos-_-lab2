"""
Gestor de respaldos ZIP para la Agenda de Contactos.

Permite crear respaldos comprimidos de los archivos de datos,
listar respaldos existentes, y restaurar desde un respaldo previo.

Los respaldos incluyen:
  - contactos.dat   (archivo de registros)
  - indice.json     (índice primario)
  - contactos.sha256 (hash de integridad)

Antes de restaurar, se crea automáticamente un respaldo de
seguridad del estado actual.
"""

import os
import zipfile
import logging
from datetime import datetime

import sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from config import (
    BACKUPS_DIR, DATA_DIR, CONTACTS_FILE, INDEX_FILE, HASH_FILE
)

logger = logging.getLogger(__name__)


class BackupManager:
    """
    Gestiona la creación, listado y restauración de respaldos ZIP.
    """

    def __init__(self, contact_service):
        """
        Inicializa el gestor de respaldos.

        Args:
            contact_service: Instancia de ContactService.
        """
        self.contact_service = contact_service
        self.backups_dir = BACKUPS_DIR
        self.data_dir = DATA_DIR

        # Asegurar que exista el directorio de respaldos
        os.makedirs(self.backups_dir, exist_ok=True)

    def create_backup(self) -> tuple[bool, str, dict]:
        """
        Crea un respaldo ZIP de los archivos de datos.

        Incluye contactos.dat, indice.json y contactos.sha256
        en un archivo ZIP con marca de tiempo en el nombre.

        Returns:
            Tupla (éxito, mensaje, info):
              - info: dict con 'filepath', 'original_size',
                      'compressed_size'
        """
        empty_info = {'filepath': '', 'original_size': 0, 'compressed_size': 0}

        try:
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            zip_filename = f"backup_{timestamp}.zip"
            zip_filepath = os.path.join(self.backups_dir, zip_filename)

            # Archivos a respaldar
            files_to_backup = [
                ('contactos.dat', CONTACTS_FILE),
                ('indice.json', INDEX_FILE),
                ('contactos.sha256', HASH_FILE),
            ]

            original_size = 0
            files_added = 0

            with zipfile.ZipFile(
                zip_filepath, 'w', zipfile.ZIP_DEFLATED
            ) as zf:
                for arcname, filepath in files_to_backup:
                    if os.path.exists(filepath):
                        file_size = os.path.getsize(filepath)
                        original_size += file_size
                        zf.write(filepath, arcname)
                        files_added += 1
                        logger.debug(
                            "Añadido al respaldo: %s (%d bytes)",
                            arcname, file_size
                        )
                    else:
                        logger.warning(
                            "Archivo no encontrado para respaldo: %s",
                            filepath
                        )

            if files_added == 0:
                # Eliminar ZIP vacío
                try:
                    os.unlink(zip_filepath)
                except OSError:
                    pass
                return (
                    False,
                    "No se encontraron archivos para respaldar",
                    empty_info
                )

            compressed_size = os.path.getsize(zip_filepath)

            info = {
                'filepath': zip_filepath,
                'original_size': original_size,
                'compressed_size': compressed_size,
            }

            # Calcular ratio de compresión
            if original_size > 0:
                ratio = (1 - compressed_size / original_size) * 100
                size_msg = (
                    f"Tamaño original: {original_size:,} bytes | "
                    f"Comprimido: {compressed_size:,} bytes | "
                    f"Reducción: {ratio:.1f}%"
                )
            else:
                size_msg = f"Tamaño comprimido: {compressed_size:,} bytes"

            logger.info(
                "Respaldo creado: %s (%d archivos). %s",
                zip_filepath, files_added, size_msg
            )

            return (
                True,
                f"Respaldo creado exitosamente: {zip_filename}\n"
                f"{files_added} archivos respaldados.\n{size_msg}",
                info
            )

        except (OSError, PermissionError) as exc:
            logger.error("Error al crear respaldo: %s", exc)
            return (False, f"Error al crear respaldo: {exc}", empty_info)
        except Exception as exc:
            logger.error("Error inesperado al crear respaldo: %s", exc)
            return (False, f"Error inesperado: {exc}", empty_info)

    def list_backups(self) -> list[dict]:
        """
        Lista todos los respaldos ZIP disponibles.

        Returns:
            Lista de diccionarios con:
              - filename: nombre del archivo
              - filepath: ruta completa
              - size:     tamaño en bytes
              - created:  fecha de creación (ISO string)
        """
        backups = []

        try:
            if not os.path.exists(self.backups_dir):
                return backups

            for filename in sorted(os.listdir(self.backups_dir)):
                if not filename.endswith('.zip'):
                    continue

                filepath = os.path.join(self.backups_dir, filename)

                try:
                    stat = os.stat(filepath)
                    size = stat.st_size
                    created = datetime.fromtimestamp(
                        stat.st_mtime
                    ).isoformat()

                    # Intentar extraer fecha del nombre del archivo
                    # Formato: backup_YYYYMMDD_HHMMSS.zip
                    try:
                        parts = filename.replace('backup_', '').replace(
                            '.zip', ''
                        )
                        dt = datetime.strptime(parts, '%Y%m%d_%H%M%S')
                        created = dt.isoformat()
                    except (ValueError, IndexError):
                        pass  # Usar fecha del archivo

                    backups.append({
                        'filename': filename,
                        'filepath': filepath,
                        'size': size,
                        'created': created,
                    })

                except OSError as exc:
                    logger.warning(
                        "No se pudo obtener info de %s: %s",
                        filename, exc
                    )

            logger.debug("Se encontraron %d respaldos", len(backups))

        except (OSError, PermissionError) as exc:
            logger.error("Error al listar respaldos: %s", exc)

        return backups

    def restore_backup(self, filepath: str) -> tuple[bool, str]:
        """
        Restaura un respaldo ZIP.

        Antes de restaurar, crea un respaldo de seguridad del estado
        actual.  Luego extrae los archivos del ZIP al directorio de
        datos y recarga el índice.

        Args:
            filepath: Ruta al archivo ZIP a restaurar.

        Returns:
            Tupla (éxito, mensaje).
        """
        try:
            # Validar respaldo primero
            valid, validation_msg = self.validate_backup(filepath)
            if not valid:
                return (False, f"Respaldo inválido: {validation_msg}")

            # Crear respaldo de seguridad del estado actual
            logger.info("Creando respaldo de seguridad antes de restaurar...")
            safety_ok, safety_msg, _ = self.create_backup()
            if safety_ok:
                logger.info("Respaldo de seguridad creado: %s", safety_msg)
            else:
                logger.warning(
                    "No se pudo crear respaldo de seguridad: %s", safety_msg
                )
                # Continuar de todos modos si no hay datos actuales

            # Extraer archivos del respaldo
            with zipfile.ZipFile(filepath, 'r') as zf:
                zf.extractall(self.data_dir)
                extracted = zf.namelist()

            logger.info(
                "Respaldo restaurado: %d archivos extraídos de %s",
                len(extracted), filepath
            )

            # Recargar el índice
            try:
                self.contact_service.index_manager = type(
                    self.contact_service.index_manager
                )(INDEX_FILE)
                logger.info("Índice recargado después de restauración")
            except Exception as exc:
                logger.warning(
                    "Error al recargar índice: %s. "
                    "Se recomienda reconstruir el índice.", exc
                )

            # Verificar integridad
            try:
                ok, integrity_msg = self.contact_service.verify_integrity()
                if ok:
                    logger.info("Integridad post-restauración: %s", integrity_msg)
                else:
                    logger.warning(
                        "Integridad post-restauración: %s", integrity_msg
                    )
            except Exception as exc:
                logger.warning(
                    "No se pudo verificar integridad post-restauración: %s",
                    exc
                )

            return (
                True,
                f"Respaldo restaurado exitosamente.\n"
                f"Archivos extraídos: {', '.join(extracted)}"
            )

        except zipfile.BadZipFile:
            return (False, "El archivo ZIP está corrupto o no es válido")
        except (OSError, PermissionError) as exc:
            logger.error("Error al restaurar respaldo: %s", exc)
            return (False, f"Error al restaurar: {exc}")
        except Exception as exc:
            logger.error("Error inesperado al restaurar: %s", exc)
            return (False, f"Error inesperado: {exc}")

    def validate_backup(self, filepath: str) -> tuple[bool, str]:
        """
        Valida que un archivo ZIP sea un respaldo válido.

        Verifica que:
          - El archivo existe
          - Es un ZIP válido
          - Contiene al menos contactos.dat

        Args:
            filepath: Ruta al archivo ZIP a validar.

        Returns:
            Tupla (válido, mensaje).
        """
        if not filepath:
            return (False, "No se proporcionó ruta de archivo")

        if not os.path.exists(filepath):
            return (False, f"Archivo no encontrado: {filepath}")

        try:
            if not zipfile.is_zipfile(filepath):
                return (False, "El archivo no es un ZIP válido")

            with zipfile.ZipFile(filepath, 'r') as zf:
                # Verificar integridad del ZIP
                bad_file = zf.testzip()
                if bad_file is not None:
                    return (
                        False,
                        f"Archivo corrupto dentro del ZIP: {bad_file}"
                    )

                contents = zf.namelist()

                # Verificar que contenga contactos.dat
                if 'contactos.dat' not in contents:
                    return (
                        False,
                        "El respaldo no contiene 'contactos.dat'. "
                        f"Contenido: {', '.join(contents)}"
                    )

                logger.debug(
                    "Respaldo válido: %s (contenido: %s)",
                    filepath, ', '.join(contents)
                )

                return (
                    True,
                    f"Respaldo válido. Contiene: {', '.join(contents)}"
                )

        except zipfile.BadZipFile:
            return (False, "El archivo ZIP está corrupto")
        except (OSError, PermissionError) as exc:
            return (False, f"Error al leer archivo: {exc}")
