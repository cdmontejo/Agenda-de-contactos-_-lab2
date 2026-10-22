"""
Servicio de importación inteligente desde archivos CSV para ContactHub Enterprise.
Permite previsualizar datos, mapear columnas, detectar colisiones de ID y ejecutar
inserciones en bloque con actualización atómica de índice y sellos SHA-256.
"""

import csv
import logging
from pathlib import Path
from typing import Tuple, List, Dict, Any, Optional

import sys
sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent))
from src.core.validators import validate_contact

logger = logging.getLogger("services.import_service")


class ImportService:
    """
    Gestor del proceso controlado de importación de contactos.
    """

    def __init__(self, contact_service=None):
        self.contact_service = contact_service

    def preview_csv(self, filepath: Path | str, delimiter: str = ",") -> Tuple[bool, str, Dict[str, Any]]:
        """
        Lee la estructura de un archivo CSV y retorna las columnas detectadas,
        una muestra de las primeras 5 filas y el conteo total estimado.
        """
        fpath = Path(filepath)
        if not fpath.exists():
            return False, f"El archivo '{fpath.name}' no fue encontrado.", {}

        try:
            # Detección de encoding (intentar utf-8-sig primero para BOM, luego utf-8, luego latin-1)
            encoding = "utf-8-sig"
            try:
                with open(fpath, "r", encoding=encoding) as f:
                    sample = f.read(2048)
            except UnicodeDecodeError:
                encoding = "latin-1"

            with open(fpath, "r", encoding=encoding) as f:
                reader = csv.reader(f, delimiter=delimiter)
                headers = next(reader, None)
                if not headers:
                    return False, "El archivo CSV está vacío.", {}

                # Limpiar encabezados
                headers = [h.strip() for h in headers]

                sample_rows = []
                total_rows = 0
                for row in reader:
                    if row and any(cell.strip() for cell in row):
                        total_rows += 1
                        if len(sample_rows) < 5:
                            sample_rows.append(row)

            info = {
                "headers": headers,
                "sample_rows": sample_rows,
                "total_rows": total_rows,
                "encoding": encoding,
                "filename": fpath.name
            }
            return True, f"CSV analizado: {total_rows} filas encontradas.", info

        except Exception as exc:
            logger.error("Error al previsualizar CSV: %s", exc)
            return False, f"Fallo al leer archivo CSV: {exc}", {}

    def execute_import(self, filepath: Path | str, mapping: Dict[str, str],
                       delimiter: str = ",") -> Tuple[bool, str, Dict[str, Any]]:
        """
        Ejecuta la importación mapeando las columnas del CSV a los campos requeridos:
        'id', 'nombre', 'telefono', 'correo', 'ciudad'.
        """
        if not self.contact_service:
            return False, "Servicio de contactos no disponible.", {}

        fpath = Path(filepath)
        if not fpath.exists():
            return False, f"Archivo {fpath.name} no encontrado.", {}

        try:
            encoding = "utf-8-sig"
            try:
                with open(fpath, "r", encoding=encoding) as f:
                    f.read(1024)
            except UnicodeDecodeError:
                encoding = "latin-1"

            with open(fpath, "r", encoding=encoding) as f:
                reader = csv.DictReader(f, delimiter=delimiter)

                imported_count = 0
                skipped_duplicates = 0
                validation_errors = 0
                error_details = []

                for row_idx, row in enumerate(reader, start=2):
                    # Mapear columnas según el diccionario proporcionado
                    raw_id = row.get(mapping.get("id", "ID"), "").strip()
                    nombre = row.get(mapping.get("nombre", "Nombre"), "").strip()
                    telefono = row.get(mapping.get("telefono", "Teléfono"), "").strip()
                    correo = row.get(mapping.get("correo", "Correo"), "").strip()
                    ciudad = row.get(mapping.get("ciudad", "Ciudad"), "").strip()

                    contact_data = {
                        "id": raw_id,
                        "nombre": nombre,
                        "telefono": telefono,
                        "correo": correo,
                        "ciudad": ciudad,
                        "estado": "A"
                    }

                    # Validar
                    is_valid, errors = validate_contact(contact_data)
                    if not is_valid:
                        validation_errors += 1
                        error_details.append(f"Fila {row_idx}: {', '.join(errors)}")
                        continue

                    # Comprobar duplicado en índice
                    if self.contact_service.index_manager.has(raw_id):
                        skipped_duplicates += 1
                        error_details.append(f"Fila {row_idx}: ID {raw_id} duplicado (omitido).")
                        continue

                    # Guardar registro
                    ok, msg, _ = self.contact_service.add_contact(contact_data)
                    if ok:
                        imported_count += 1
                    else:
                        validation_errors += 1
                        error_details.append(f"Fila {row_idx}: {msg}")

            summary = {
                "imported": imported_count,
                "skipped_duplicates": skipped_duplicates,
                "validation_errors": validation_errors,
                "errors_sample": error_details[:10]
            }

            msg = (
                f"Importación completada: {imported_count} contactos añadidos. "
                f"({skipped_duplicates} duplicados omitidos, {validation_errors} errores)."
            )
            logger.info(msg)
            return True, msg, summary

        except Exception as exc:
            logger.error("Error durante ejecución de importación CSV: %s", exc)
            return False, f"Fallo al procesar importación: {exc}", {}
