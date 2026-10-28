"""
Servicio de respaldos comprimidos ZIP y Time Machine para ContactHub Enterprise.
Empaqueta contactos.dat, indice.json y contactos.sha256 con compresión DEFLATE.
Permite restauración segura creando un snapshot previo de contingencia.
"""

import os
import shutil
import zipfile
import logging
from datetime import datetime
from pathlib import Path
from typing import Dict, Any, List, Tuple

import sys
sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent))
from config import BACKUPS_DIR, DATA_DIR, CONTACTS_FILE, INDEX_FILE, HASH_FILE

logger = logging.getLogger("services.backup_service")


class BackupService:
    """
    Gestor de copias de seguridad ZIP, catálogo histórico y restauración asistida.
    """

    def __init__(self, contact_service=None, backups_dir: Path | str = BACKUPS_DIR):
        self.contact_service = contact_service
        self.backups_dir = Path(backups_dir)
        self.backups_dir.mkdir(parents=True, exist_ok=True)

    def create_backup(self, note: str = "") -> Tuple[bool, str, Dict[str, Any]]:
        """
        Crea un respaldo comprimido ZIP con marca de tiempo.
        Calcula el ratio de compresión y metadatos del archivo generado.
        """
        empty_info = {"filepath": "", "original_size": 0, "compressed_size": 0, "ratio": 0.0}

        try:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            zip_filename = f"backup_{timestamp}.zip"
            zip_path = self.backups_dir / zip_filename

            files_to_pack = [
                ("contactos.dat", CONTACTS_FILE),
                ("indice.json", INDEX_FILE),
                ("contactos.sha256", HASH_FILE)
            ]

            original_size = 0
            with zipfile.ZipFile(zip_path, "w", zipfile.ZIP_DEFLATED) as zipf:
                for arcname, fpath in files_to_pack:
                    if fpath.exists():
                        f_size = fpath.stat().st_size
                        original_size += f_size
                        zipf.write(fpath, arcname=arcname)

            compressed_size = zip_path.stat().st_size if zip_path.exists() else 0
            ratio = ((original_size - compressed_size) / original_size * 100) if original_size > 0 else 0.0

            info = {
                "filename": zip_filename,
                "filepath": str(zip_path),
                "original_size": original_size,
                "compressed_size": compressed_size,
                "reduction_percentage": round(ratio, 1),
                "timestamp": timestamp,
                "note": note
            }

            msg = (
                f"Respaldo creado: {zip_filename} | "
                f"Original: {original_size:,} B -> Comprimido: {compressed_size:,} B (Ahorro: {ratio:.1f}%)"
            )
            logger.info(msg)
            return True, msg, info

        except Exception as exc:
            logger.error("Error al generar respaldo ZIP: %s", exc)
            return False, f"Fallo al crear respaldo: {exc}", empty_info

    def list_backups(self) -> List[Dict[str, Any]]:
        """Retorna la lista ordenada de respaldos existentes en el directorio."""
        backups = []
        if not self.backups_dir.exists():
            return backups

        for zip_file in sorted(self.backups_dir.glob("backup_*.zip"), reverse=True):
            try:
                stat = zip_file.stat()
                mtime = datetime.fromtimestamp(stat.st_mtime).strftime("%Y-%m-%d %H:%M:%S")

                # Inspección interna del ZIP
                with zipfile.ZipFile(zip_file, "r") as zf:
                    file_list = zf.namelist()
                    uncompressed_total = sum(zinfo.file_size for zinfo in zf.infolist())

                backups.append({
                    "filename": zip_file.name,
                    "filepath": str(zip_file),
                    "size_bytes": stat.st_size,
                    "size_formatted": f"{stat.st_size / 1024:.1f} KB",
                    "original_size": uncompressed_total,
                    "date": mtime,
                    "files_count": len(file_list),
                    "is_valid": ("contactos.dat" in file_list)
                })
            except Exception as exc:
                logger.warning("Error leyendo metadata de %s: %s", zip_file.name, exc)

        return backups

    def restore_backup(self, zip_filename: str) -> Tuple[bool, str]:
        """
        Restaura un respaldo ZIP aplicando Safe Restore:
        1. Crea un respaldo de seguridad del estado actual antes de tocar nada.
        2. Extrae los archivos del ZIP sobre la carpeta data/.
        3. Recarga el índice y verifica la integridad SHA-256.
        """
        zip_path = self.backups_dir / zip_filename
        if not zip_path.exists():
            return False, f"El archivo de respaldo '{zip_filename}' no existe."

        try:
            # 1. Crear backup preventivo
            logger.info("Iniciando restauración. Creando backup preventivo de seguridad...")
            self.create_backup(note="Snapshot preventivo antes de restauración")

            # 2. Validar que el ZIP contenga los archivos mínimos
            with zipfile.ZipFile(zip_path, "r") as zf:
                namelist = zf.namelist()
                if "contactos.dat" not in namelist:
                    return False, "El archivo ZIP no contiene 'contactos.dat' válido."
                
                # Extraer de forma segura a data/
                zf.extractall(DATA_DIR)

            # 3. Recargar servicios si están vinculados
            if self.contact_service:
                self.contact_service.record_manager._ensure_file_exists()
                self.contact_service.index_manager.load()
                self.contact_service.integrity_manager.verify()

            msg = f"Sistema restaurado exitosamente desde '{zip_filename}'."
            logger.info(msg)
            return True, msg

        except Exception as exc:
            logger.critical("Error crítico durante la restauración de respaldo: %s", exc)
            return False, f"Fallo al restaurar respaldo: {exc}"

