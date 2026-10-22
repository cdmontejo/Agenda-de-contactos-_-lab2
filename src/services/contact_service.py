"""
Servicio central de orquestación de contactos para ContactHub Enterprise.
Coordina RecordManager, IndexManager e IntegrityManager para proveer
todas las operaciones CRUD, acceso aleatorio, búsqueda, inspección y auditoría.
"""

import os
import logging
from pathlib import Path
from typing import Dict, Any, List, Optional, Tuple

import sys
sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent))
from config import CONTACTS_FILE, INDEX_FILE, HASH_FILE, RECORD_SIZE
from src.storage.record_manager import RecordManager
from src.storage.index_manager import IndexManager
from src.storage.integrity_manager import IntegrityManager
from src.core.validators import validate_contact

logger = logging.getLogger("services.contact_service")


class ContactService:
    """
    Servicio de negocio que orquesta la persistencia física, el índice y los sellos de seguridad.
    """

    def __init__(self, data_file: Path | str = CONTACTS_FILE,
                 index_file: Path | str = INDEX_FILE,
                 hash_file: Path | str = HASH_FILE):
        self.record_manager = RecordManager(data_file)
        self.index_manager = IndexManager(index_file)
        self.integrity_manager = IntegrityManager(data_file, hash_file)

        # Si el archivo tiene registros pero el índice está vacío, lo reconstruye
        if self.record_manager.get_total_records() > 0 and self.index_manager.count() == 0:
            logger.info("Índice vacío con registros en disco detectado; reconstruyendo índice...")
            self.rebuild_index()

    def add_contact(self, data: Dict[str, Any]) -> Tuple[bool, str, Optional[Dict[str, Any]]]:
        """
        Añade un nuevo contacto.
        1. Valida campos y longitudes en bytes UTF-8.
        2. Verifica unicidad de ID en el índice O(1).
        3. Escribe en disco con seek() y tell().
        4. Actualiza indice.json.
        5. Recalcula y guarda el sello SHA-256.
        """
        is_valid, errors = validate_contact(data)
        if not is_valid:
            return False, "Errores de validación:\n• " + "\n• ".join(errors), None

        cid = str(data.get("id")).strip()
        if self.index_manager.has(cid):
            return False, f"El ID {cid} ya existe en el sistema. Utilice un ID único.", None

        contact_record = {
            "id": cid,
            "nombre": str(data.get("nombre", "")).strip(),
            "telefono": str(data.get("telefono", "")).strip(),
            "correo": str(data.get("correo", "")).strip(),
            "ciudad": str(data.get("ciudad", "")).strip(),
            "estado": "A"
        }

        try:
            record_num, pos_ini, pos_fin = self.record_manager.add_record(contact_record)
            self.index_manager.add(cid, record_num)
            self.integrity_manager.save_hash()

            info = {
                "record_num": record_num,
                "byte_offset": pos_ini,
                "tell_after": pos_fin,
                **contact_record
            }
            logger.info("Contacto ID %s añadido con éxito en record #%d (offset %d)", cid, record_num, pos_ini)
            return True, f"Contacto '{contact_record['nombre']}' registrado exitosamente (Offset: {pos_ini} B).", info
        except Exception as exc:
            logger.error("Fallo al registrar contacto: %s", exc)
            return False, f"Error interno al escribir en disco: {exc}", None

    def get_contact_by_id(self, contact_id: Any) -> Tuple[bool, str, Optional[Dict[str, Any]]]:
        """
        Búsqueda por acceso directo aleatorio O(1) asistida por índice.
        Obtiene el record_num desde indice.json y ejecuta f.seek(record_num * 256).
        """
        cid = str(contact_id).strip()
        record_num = self.index_manager.get(cid)

        if record_num is None:
            return False, f"Contacto con ID {cid} no encontrado en el índice primario.", None

        contact, tell_antes, tell_despues = self.record_manager.read_record(record_num)
        if not contact:
            return False, f"No se pudo leer el registro #{record_num} en disco.", None

        contact["record_num"] = record_num
        contact["byte_offset"] = tell_antes
        contact["tell_after"] = tell_despues
        return True, "Contacto encontrado.", contact

    def update_contact(self, data: Dict[str, Any]) -> Tuple[bool, str, Optional[Dict[str, Any]]]:
        """
        Modificación in-place en disco de un contacto existente.
        Sobrescribe únicamente los 256 bytes correspondientes y actualiza el hash SHA-256.
        """
        is_valid, errors = validate_contact(data)
        if not is_valid:
            return False, "Errores de validación:\n• " + "\n• ".join(errors), None

        cid = str(data.get("id")).strip()
        record_num = self.index_manager.get(cid)

        if record_num is None:
            return False, f"El contacto con ID {cid} no existe para modificar.", None

        contact_record = {
            "id": cid,
            "nombre": str(data.get("nombre", "")).strip(),
            "telefono": str(data.get("telefono", "")).strip(),
            "correo": str(data.get("correo", "")).strip(),
            "ciudad": str(data.get("ciudad", "")).strip(),
            "estado": "A"
        }

        try:
            tell_antes, tell_despues = self.record_manager.update_record(record_num, contact_record)
            self.integrity_manager.save_hash()

            info = {
                "record_num": record_num,
                "byte_offset": tell_antes,
                "tell_after": tell_despues,
                **contact_record
            }
            logger.info("Contacto ID %s actualizado in-place en record #%d", cid, record_num)
            return True, f"Contacto '{contact_record['nombre']}' modificado in-place correctamente.", info
        except Exception as exc:
            logger.error("Error al actualizar contacto: %s", exc)
            return False, f"Fallo al modificar en disco: {exc}", None

    def delete_contact(self, contact_id: Any) -> Tuple[bool, str]:
        """
        Eliminación lógica de un contacto.
        Marca el byte de estado como 'D' en disco in-place, lo remueve de indice.json
        y actualiza el hash de integridad.
        """
        cid = str(contact_id).strip()
        record_num = self.index_manager.get(cid)

        if record_num is None:
            return False, f"El contacto con ID {cid} no existe o ya fue eliminado."

        contact, _, _ = self.record_manager.read_record(record_num)
        if not contact:
            return False, f"No se pudo acceder al registro #{record_num} para eliminar."

        # Modificación in-place con estado 'D'
        contact["estado"] = "D"
        self.record_manager.update_record(record_num, contact)

        # Quitar del índice y actualizar hash
        self.index_manager.remove(cid)
        self.integrity_manager.save_hash()

        logger.info("Contacto ID %s marcado como eliminado ('D') y removido del índice.", cid)
        return True, f"Contacto ID {cid} eliminado lógicamente (Registro #{record_num} preservado en disco)."

    def restore_contact(self, contact_id: Any) -> Tuple[bool, str]:
        """
        Restaura un contacto previamente eliminado ('D' -> 'A') buscando en el archivo
        y reinsertándolo en el índice primario.
        """
        cid = str(contact_id).strip()
        all_records = self.record_manager.read_all_records(include_deleted=True)

        target_rec_num = None
        target_contact = None

        for rec_num, contact in all_records:
            if str(contact.get("id")) == cid:
                target_rec_num = rec_num
                target_contact = contact
                break

        if target_rec_num is None or target_contact is None:
            return False, f"No se encontró ningún registro para el ID {cid} en el archivo físico."

        if target_contact.get("estado") == "A":
            return False, f"El contacto ID {cid} ya se encuentra activo."

        target_contact["estado"] = "A"
        self.record_manager.update_record(target_rec_num, target_contact)
        self.index_manager.add(cid, target_rec_num)
        self.integrity_manager.save_hash()

        return True, f"Contacto ID {cid} ('{target_contact['nombre']}') restaurado exitosamente a estado Activo."

    def get_all_contacts(self, include_deleted: bool = False) -> List[Dict[str, Any]]:
        """Retorna todos los contactos del archivo con sus metadatos de offset y número de registro."""
        records = self.record_manager.read_all_records(include_deleted=include_deleted)
        contacts = []
        for rec_num, c in records:
            c["record_num"] = rec_num
            c["byte_offset"] = rec_num * RECORD_SIZE
            contacts.append(c)
        return contacts

    def search_contacts(self, query: str = "", field: str = "todos",
                        status_filter: str = "activos") -> List[Dict[str, Any]]:
        """
        Búsqueda multicriterio con filtrado por campo y estado.
        """
        include_del = (status_filter.lower() in ("todos", "eliminados"))
        all_contacts = self.get_all_contacts(include_deleted=include_del)

        if status_filter.lower() == "activos":
            candidates = [c for c in all_contacts if c.get("estado") == "A"]
        elif status_filter.lower() == "eliminados":
            candidates = [c for c in all_contacts if c.get("estado") == "D"]
        else:
            candidates = all_contacts

        q = query.strip().lower()
        if not q:
            return candidates

        results = []
        for c in candidates:
            match = False
            if field == "id":
                match = q in str(c.get("id", "")).lower()
            elif field == "nombre":
                match = q in str(c.get("nombre", "")).lower()
            elif field == "telefono":
                match = q in str(c.get("telefono", "")).lower()
            elif field == "correo":
                match = q in str(c.get("correo", "")).lower()
            elif field == "ciudad":
                match = q in str(c.get("ciudad", "")).lower()
            else:  # todos los campos
                match = (
                    q in str(c.get("id", "")).lower() or
                    q in str(c.get("nombre", "")).lower() or
                    q in str(c.get("telefono", "")).lower() or
                    q in str(c.get("correo", "")).lower() or
                    q in str(c.get("ciudad", "")).lower()
                )
            if match:
                results.append(c)
        return results

    def get_contact_inspection(self, contact_id: Any) -> Optional[Dict[str, Any]]:
        """
        Retorna la inspección profunda para demostración didáctica de bajo nivel:
        Byte offset, tell() pointers, hex view y ASCII view de los 256 bytes exactos.
        """
        cid = str(contact_id).strip()
        record_num = self.index_manager.get(cid)

        # Si no está en el índice activo, buscar en registros globales
        if record_num is None:
            for r_num, c in self.record_manager.read_all_records(include_deleted=True):
                if str(c.get("id")) == cid:
                    record_num = r_num
                    break

        if record_num is None:
            return None

        contact, tell_antes, tell_despues = self.record_manager.read_record(record_num)
        raw_bytes = self.record_manager.read_raw_bytes(record_num)

        # Generar vista Hexadecimal formateada en líneas de 16 bytes
        hex_lines = []
        for i in range(0, len(raw_bytes), 16):
            chunk = raw_bytes[i:i + 16]
            hex_part = " ".join(f"{b:02X}" for b in chunk)
            ascii_part = "".join(chr(b) if 32 <= b <= 126 else "." for b in chunk)
            hex_lines.append(f"{i:04X}  {hex_part:<48}  |{ascii_part}|")

        return {
            "record_num": record_num,
            "byte_offset": record_num * RECORD_SIZE,
            "tell_antes": tell_antes,
            "tell_despues": tell_despues,
            "total_bytes": len(raw_bytes),
            "hex_dump": "\n".join(hex_lines),
            "contact": contact
        }

    def rebuild_index(self) -> Tuple[bool, str, int]:
        """
        Reconstruye indice.json leyendo secuencialmente los 256 bytes de cada registro en disco.
        Recalcula también el sello SHA-256.
        """
        try:
            records = self.record_manager.read_all_records(include_deleted=True)
            count = self.index_manager.rebuild(records)
            self.integrity_manager.save_hash()
            return True, f"Índice reconstruido con éxito ({count} registros activos indexados).", count
        except Exception as exc:
            logger.error("Fallo al reconstruir índice: %s", exc)
            return False, f"Error al reconstruir índice: {exc}", 0

    def get_statistics(self) -> Dict[str, Any]:
        """Retorna métricas cuantitativas consolidadas para el Dashboard."""
        all_contacts = self.get_all_contacts(include_deleted=True)
        activos = [c for c in all_contacts if c.get("estado") == "A"]
        eliminados = [c for c in all_contacts if c.get("estado") == "D"]

        ciudades_dist = {}
        for c in activos:
            cd = c.get("ciudad", "Desconocida") or "Desconocida"
            ciudades_dist[cd] = ciudades_dist.get(cd, 0) + 1

        file_size = self.record_manager.filepath.stat().st_size if self.record_manager.filepath.exists() else 0
        total_records = file_size // RECORD_SIZE

        return {
            "total_activos": len(activos),
            "total_eliminados": len(eliminados),
            "total_registros_fisicos": total_records,
            "tamano_archivo_bytes": file_size,
            "distribucion_ciudades": ciudades_dist,
            "contactos_recientes": activos[-5:] if activos else []
        }
