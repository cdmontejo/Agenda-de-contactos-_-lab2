"""
Servicio central de gestión de contactos.

Orquesta RecordManager, IndexManager e IntegrityManager para
proporcionar operaciones CRUD completas sobre los contactos.

Todas las operaciones retornan tuplas (éxito, mensaje) para
facilitar el manejo desde la interfaz gráfica.
"""

import logging

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from config import CONTACTS_FILE, INDEX_FILE, HASH_FILE
from storage.record_manager import RecordManager
from storage.index_manager import IndexManager
from storage.integrity import IntegrityManager
from services.validators import validate_contact

logger = logging.getLogger(__name__)


class ContactService:
    """
    Servicio de lógica de negocio para la gestión de contactos.

    Coordina las capas de almacenamiento (registros, índice, hash)
    y aplica validaciones antes de cada operación.
    """

    def __init__(self):
        """
        Inicializa el servicio con todas las dependencias.

        Crea instancias de RecordManager, IndexManager e
        IntegrityManager.  Verifica la integridad al inicio y
        registra el resultado (sin detener la aplicación si falla).
        """
        self.record_manager = RecordManager(CONTACTS_FILE)
        self.index_manager = IndexManager(INDEX_FILE)
        self.integrity_manager = IntegrityManager(CONTACTS_FILE, HASH_FILE)

        # Verificar integridad al iniciar
        try:
            ok, msg = self.integrity_manager.verify()
            if ok:
                logger.info("Verificación de integridad al inicio: %s", msg)
            else:
                logger.warning(
                    "Verificación de integridad al inicio: %s", msg
                )
        except Exception as exc:
            logger.warning(
                "No se pudo verificar integridad al inicio: %s", exc
            )

    def add_contact(self, data: dict) -> tuple[bool, str]:
        """
        Añade un nuevo contacto al sistema.

        Valida los datos, verifica que el ID no exista, añade el
        registro al archivo, actualiza el índice y recalcula el hash.

        Args:
            data: Diccionario con id, nombre, telefono, correo, ciudad.

        Returns:
            Tupla (éxito, mensaje).
        """
        try:
            # Validar datos
            valid, errors = validate_contact(data)
            if not valid:
                return (False, "Errores de validación:\n" + "\n".join(errors))

            contact_id = int(data['id'])

            # Verificar que el ID no exista
            if self.index_manager.has(contact_id):
                return (
                    False,
                    f"El ID {contact_id} ya existe en la agenda. "
                    f"Use un ID diferente."
                )

            # Preparar registro
            contact = {
                'id': str(contact_id),
                'nombre': str(data['nombre']).strip(),
                'telefono': str(data['telefono']).strip(),
                'correo': str(data['correo']).strip(),
                'ciudad': str(data['ciudad']).strip(),
                'estado': 'A',
            }

            # Añadir registro al archivo
            record_num = self.record_manager.add_record(contact)

            # Actualizar índice
            self.index_manager.add(contact_id, record_num)

            # Actualizar hash de integridad
            self.integrity_manager.update()

            logger.info(
                "Contacto añadido: ID=%d, nombre='%s', registro=#%d",
                contact_id, contact['nombre'], record_num
            )

            return (
                True,
                f"Contacto '{contact['nombre']}' (ID: {contact_id}) "
                f"añadido exitosamente en registro #{record_num}"
            )

        except Exception as exc:
            logger.error("Error al añadir contacto: %s", exc)
            return (False, f"Error inesperado al añadir contacto: {exc}")

    def search_by_id(self, contact_id: int) -> dict | None:
        """
        Busca un contacto por su ID usando el índice primario.

        Primero consulta el índice para obtener el número de registro,
        luego hace seek directo al registro en el archivo.

        Args:
            contact_id: ID del contacto a buscar.

        Returns:
            Diccionario con los datos del contacto, o ``None``.
        """
        try:
            # Buscar en el índice
            logger.info(
                "Buscando contacto ID=%d en el índice...", contact_id
            )
            record_num = self.index_manager.get(contact_id)

            if record_num is None:
                logger.info("ID=%d no encontrado en el índice", contact_id)
                return None

            logger.info(
                "ID=%d encontrado en índice -> registro #%d. "
                "Haciendo seek directo...",
                contact_id, record_num
            )

            # Leer registro directamente
            contact = self.record_manager.read_record(record_num)
            return contact

        except Exception as exc:
            logger.error("Error al buscar contacto ID=%d: %s", contact_id, exc)
            return None

    def update_contact(self, contact_id: int, new_data: dict) -> tuple[bool, str]:
        """
        Actualiza un contacto existente.

        Busca el registro por ID, valida los nuevos datos, actualiza
        el registro en su posición exacta y recalcula el hash.

        Args:
            contact_id: ID del contacto a actualizar.
            new_data:   Diccionario con los nuevos datos.

        Returns:
            Tupla (éxito, mensaje).
        """
        try:
            # Buscar registro en el índice
            record_num = self.index_manager.get(contact_id)
            if record_num is None:
                return (
                    False,
                    f"Contacto con ID {contact_id} no encontrado"
                )

            # Leer registro actual para preservar estado
            current = self.record_manager.read_record(record_num)
            if current is None:
                return (False, "Error al leer el registro actual")

            # Preparar datos actualizados con el ID original
            updated_data = {
                'id': str(contact_id),
                'nombre': str(new_data.get('nombre', current['nombre'])).strip(),
                'telefono': str(new_data.get('telefono', current['telefono'])).strip(),
                'correo': str(new_data.get('correo', current['correo'])).strip(),
                'ciudad': str(new_data.get('ciudad', current['ciudad'])).strip(),
            }

            # Validar datos actualizados
            valid, errors = validate_contact(updated_data)
            if not valid:
                return (False, "Errores de validación:\n" + "\n".join(errors))

            # Preservar el estado actual (activo/eliminado)
            updated_data['estado'] = current.get('estado', 'A')

            # Actualizar registro en el archivo
            self.record_manager.update_record(record_num, updated_data)

            # Actualizar hash
            self.integrity_manager.update()

            logger.info(
                "Contacto ID=%d actualizado en registro #%d",
                contact_id, record_num
            )

            return (
                True,
                f"Contacto ID {contact_id} actualizado exitosamente"
            )

        except Exception as exc:
            logger.error(
                "Error al actualizar contacto ID=%d: %s", contact_id, exc
            )
            return (False, f"Error inesperado al actualizar: {exc}")

    def delete_contact(self, contact_id: int) -> tuple[bool, str]:
        """
        Realiza una eliminación lógica de un contacto.

        Cambia el campo 'estado' de 'A' (Activo) a 'D' (Eliminado).
        El registro permanece en el archivo y en el índice.

        Args:
            contact_id: ID del contacto a eliminar.

        Returns:
            Tupla (éxito, mensaje).
        """
        try:
            record_num = self.index_manager.get(contact_id)
            if record_num is None:
                return (
                    False,
                    f"Contacto con ID {contact_id} no encontrado"
                )

            # Leer registro actual
            contact = self.record_manager.read_record(record_num)
            if contact is None:
                return (False, "Error al leer el registro")

            if contact.get('estado') == 'D':
                return (
                    False,
                    f"El contacto ID {contact_id} ya está eliminado"
                )

            # Cambiar estado a eliminado
            contact['estado'] = 'D'
            self.record_manager.update_record(record_num, contact)

            # Actualizar hash
            self.integrity_manager.update()

            logger.info("Contacto ID=%d eliminado lógicamente", contact_id)

            return (
                True,
                f"Contacto '{contact.get('nombre', '')}' (ID: {contact_id}) "
                f"eliminado exitosamente"
            )

        except Exception as exc:
            logger.error(
                "Error al eliminar contacto ID=%d: %s", contact_id, exc
            )
            return (False, f"Error inesperado al eliminar: {exc}")

    def restore_contact(self, contact_id: int) -> tuple[bool, str]:
        """
        Restaura un contacto previamente eliminado.

        Cambia el campo 'estado' de 'D' (Eliminado) a 'A' (Activo).

        Args:
            contact_id: ID del contacto a restaurar.

        Returns:
            Tupla (éxito, mensaje).
        """
        try:
            record_num = self.index_manager.get(contact_id)
            if record_num is None:
                return (
                    False,
                    f"Contacto con ID {contact_id} no encontrado"
                )

            contact = self.record_manager.read_record(record_num)
            if contact is None:
                return (False, "Error al leer el registro")

            if contact.get('estado') == 'A':
                return (
                    False,
                    f"El contacto ID {contact_id} ya está activo"
                )

            # Restaurar estado
            contact['estado'] = 'A'
            self.record_manager.update_record(record_num, contact)

            # Actualizar hash
            self.integrity_manager.update()

            logger.info("Contacto ID=%d restaurado", contact_id)

            return (
                True,
                f"Contacto '{contact.get('nombre', '')}' (ID: {contact_id}) "
                f"restaurado exitosamente"
            )

        except Exception as exc:
            logger.error(
                "Error al restaurar contacto ID=%d: %s", contact_id, exc
            )
            return (False, f"Error inesperado al restaurar: {exc}")

    def get_all_contacts(self, include_deleted: bool = False) -> list[dict]:
        """
        Obtiene todos los contactos del archivo.

        Args:
            include_deleted: Si es ``True``, incluye contactos con
                             estado 'D'.  Por defecto solo activos.

        Returns:
            Lista de diccionarios de contactos.
        """
        try:
            all_records = self.record_manager.read_all_records()

            if include_deleted:
                return all_records

            # Filtrar solo activos
            active = [
                r for r in all_records
                if r.get('estado', 'A') == 'A'
            ]
            return active

        except Exception as exc:
            logger.error("Error al obtener todos los contactos: %s", exc)
            return []

    def search_contacts(self, query: str, field: str = 'all') -> list[dict]:
        """
        Busca contactos activos por coincidencia parcial.

        Args:
            query: Texto a buscar (insensible a mayúsculas).
            field: Campo específico ('nombre', 'telefono', 'correo',
                   'ciudad') o 'all' para buscar en todos.

        Returns:
            Lista de contactos que coinciden con la búsqueda.
        """
        try:
            if not query or not query.strip():
                return self.get_all_contacts()

            query_lower = query.strip().lower()
            all_contacts = self.get_all_contacts(include_deleted=False)
            results = []

            searchable_fields = ['nombre', 'telefono', 'correo', 'ciudad']

            for contact in all_contacts:
                if field == 'all':
                    # Buscar en todos los campos
                    for f in searchable_fields:
                        value = contact.get(f, '').lower()
                        if query_lower in value:
                            results.append(contact)
                            break
                elif field in searchable_fields:
                    value = contact.get(field, '').lower()
                    if query_lower in value:
                        results.append(contact)

            logger.info(
                "Búsqueda '%s' en campo '%s': %d resultados",
                query, field, len(results)
            )
            return results

        except Exception as exc:
            logger.error("Error en búsqueda: %s", exc)
            return []

    def get_stats(self) -> dict:
        """
        Obtiene estadísticas del sistema de contactos.

        Returns:
            Diccionario con:
              - total:    registros totales
              - active:   registros activos
              - deleted:  registros eliminados
              - last_id:  último ID registrado (o None)
        """
        try:
            all_records = self.record_manager.read_all_records()

            total = len(all_records)
            active = sum(
                1 for r in all_records if r.get('estado', 'A') == 'A'
            )
            deleted = total - active

            # Obtener el último ID
            last_id = None
            ids = self.index_manager.get_all_ids()
            if ids:
                last_id = max(ids)

            return {
                'total': total,
                'active': active,
                'deleted': deleted,
                'last_id': last_id,
            }

        except Exception as exc:
            logger.error("Error al obtener estadísticas: %s", exc)
            return {
                'total': 0,
                'active': 0,
                'deleted': 0,
                'last_id': None,
            }

    def verify_integrity(self) -> tuple[bool, str]:
        """
        Verifica la integridad del archivo de datos.

        Delega al IntegrityManager.

        Returns:
            Tupla (éxito, mensaje).
        """
        return self.integrity_manager.verify()

    def get_file_info(self) -> dict:
        """
        Obtiene información del archivo de datos.

        Delega al RecordManager.

        Returns:
            Diccionario con información del archivo.
        """
        return self.record_manager.get_file_info()

    def rebuild_index(self) -> tuple[bool, str]:
        """
        Reconstruye el índice desde el archivo de datos.

        Útil cuando el índice está corrupto o desincronizado.

        Returns:
            Tupla (éxito, mensaje).
        """
        try:
            count = self.index_manager.rebuild(self.record_manager)
            logger.info("Índice reconstruido con %d entradas", count)
            return (
                True,
                f"Índice reconstruido exitosamente con {count} entradas"
            )
        except Exception as exc:
            logger.error("Error al reconstruir índice: %s", exc)
            return (False, f"Error al reconstruir índice: {exc}")

    def get_index_info(self) -> dict:
        """
        Obtiene información sobre el índice.

        Returns:
            Diccionario con:
              - total_entries: número de entradas en el índice
              - all_ids:       lista de todos los IDs indexados
              - index_file:    ruta del archivo de índice
        """
        return {
            'total_entries': self.index_manager.count(),
            'all_ids': self.index_manager.get_all_ids(),
            'index_file': self.index_manager.filepath,
        }
