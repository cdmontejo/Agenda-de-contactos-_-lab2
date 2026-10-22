"""
Controlador principal de la aplicación y puente MVVM entre Python y QML.
Expone propiedades reactivas, señales de estado y slots seguros para la interfaz.
"""

import os
import sys
import json
import logging
from pathlib import Path
from typing import Dict, Any, List

from PySide6.QtCore import QObject, Signal, Slot, Property

sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent))
from config import (
    APP_NAME,
    APP_VERSION,
    APP_ORGANIZATION,
    SETTINGS_FILE,
    LOG_FILE,
    CONTACTS_FILE,
    INDEX_FILE,
    HASH_FILE,
    RECORD_SIZE
)
from src.services.contact_service import ContactService
from src.services.backup_service import BackupService
from src.services.export_service import ExportService
from src.services.import_service import ImportService
from src.viewmodels.contact_model import ContactListModel

logger = logging.getLogger("viewmodels.app_controller")


class AppController(QObject):
    """
    Controlador central de la aplicación expuesto a QML como 'appController'.
    """

    statsChanged = Signal()
    integrityChanged = Signal()
    toastRequested = Signal(str, str)  # message, variant ('success', 'danger', 'info', 'warning')
    themeChanged = Signal(str)
    busyChanged = Signal()

    def __init__(self, parent=None):
        super().__init__(parent)

        # Servicios de negocio
        self._contact_service = ContactService()
        self._backup_service = BackupService(contact_service=self._contact_service)
        self._export_service = ExportService(contact_service=self._contact_service)
        self._import_service = ImportService(contact_service=self._contact_service)

        # Modelo de lista para QML
        self._contact_model = ContactListModel(self)

        # Estados reactivos
        self._current_theme = "dark"
        self._is_busy = False
        self._busy_message = ""
        self._is_integrity_valid = True
        self._stored_hash = ""
        self._calculated_hash = ""
        self._system_status_msg = "Sistema listo."

        # Cargar configuración y datos iniciales
        self._load_settings()
        self.loadContacts()
        self.verifyIntegrity()

    # ── Propiedades para QML ──────────────────────────────────────────────────

    def get_contact_model(self) -> ContactListModel:
        return self._contact_model

    contactModel = Property(QObject, get_contact_model, constant=True)

    def get_total_active(self) -> int:
        return self._contact_service.get_statistics()["total_activos"]

    totalActiveContacts = Property(int, get_total_active, notify=statsChanged)

    def get_total_deleted(self) -> int:
        return self._contact_service.get_statistics()["total_eliminados"]

    totalDeletedContacts = Property(int, get_total_deleted, notify=statsChanged)

    def get_total_physical(self) -> int:
        return self._contact_service.get_statistics()["total_registros_fisicos"]

    totalPhysicalRecords = Property(int, get_total_physical, notify=statsChanged)

    def get_file_size_bytes(self) -> int:
        return self._contact_service.get_statistics()["tamano_archivo_bytes"]

    fileSizeBytes = Property(int, get_file_size_bytes, notify=statsChanged)

    def get_file_size_formatted(self) -> str:
        b = self.get_file_size_bytes()
        if b < 1024:
            return f"{b} B"
        elif b < 1024 * 1024:
            return f"{b / 1024:.1f} KB"
        return f"{b / (1024 * 1024):.2f} MB"

    fileSizeFormatted = Property(str, get_file_size_formatted, notify=statsChanged)

    def get_is_integrity_valid(self) -> bool:
        return self._is_integrity_valid

    isIntegrityValid = Property(bool, get_is_integrity_valid, notify=integrityChanged)

    def get_stored_hash(self) -> str:
        return self._stored_hash

    storedHash = Property(str, get_stored_hash, notify=integrityChanged)

    def get_calculated_hash(self) -> str:
        return self._calculated_hash

    calculatedHash = Property(str, get_calculated_hash, notify=integrityChanged)

    def get_current_theme(self) -> str:
        return self._current_theme

    def set_current_theme(self, theme_name: str) -> None:
        if self._current_theme != theme_name:
            self._current_theme = theme_name
            self._save_settings()
            self.themeChanged.emit(theme_name)

    currentTheme = Property(str, get_current_theme, set_current_theme, notify=themeChanged)

    def get_is_busy(self) -> bool:
        return self._is_busy

    isBusy = Property(bool, get_is_busy, notify=busyChanged)

    def get_system_status_msg(self) -> str:
        return self._system_status_msg

    systemStatusMessage = Property(str, get_system_status_msg, notify=integrityChanged)

    # ── Configuración persistente ─────────────────────────────────────────────

    def _load_settings(self) -> None:
        if SETTINGS_FILE.exists():
            try:
                with open(SETTINGS_FILE, "r", encoding="utf-8") as f:
                    data = json.load(f)
                    self._current_theme = data.get("theme", "dark")
            except Exception:
                self._current_theme = "dark"

    def _save_settings(self) -> None:
        try:
            with open(SETTINGS_FILE, "w", encoding="utf-8") as f:
                json.dump({"theme": self._current_theme}, f, indent=2)
        except Exception as exc:
            logger.warning("No se pudo guardar settings.json: %s", exc)

    # ── Slots de Contactos ───────────────────────────────────────────────────

    @Slot()
    def loadContacts(self) -> None:
        """Carga los contactos activos en el modelo visual."""
        contacts = self._contact_service.search_contacts("", "todos", "activos")
        self._contact_model.set_contacts(contacts)
        self.statsChanged.emit()

    @Slot(str, str, str)
    def filterContacts(self, query: str, field: str, status: str) -> None:
        """Filtra los contactos según criterios y estado (activos/eliminados/todos)."""
        filtered = self._contact_service.search_contacts(query, field, status)
        self._contact_model.set_contacts(filtered)
        self.statsChanged.emit()

    @Slot(str, str, str, str, str, result="QVariantMap")
    def addContact(self, id_val: str, nombre: str, telefono: str, correo: str, ciudad: str) -> Dict[str, Any]:
        """Añade un nuevo contacto con cálculo directo de offsets y sellos."""
        payload = {
            "id": id_val,
            "nombre": nombre,
            "telefono": telefono,
            "correo": correo,
            "ciudad": ciudad
        }
        ok, msg, info = self._contact_service.add_contact(payload)
        if ok:
            self.loadContacts()
            self.verifyIntegrity()
            self.toastRequested.emit(msg, "success")
            return {"success": True, "message": msg, "info": info}
        else:
            self.toastRequested.emit(msg, "danger")
            return {"success": False, "message": msg, "info": {}}

    @Slot(str, str, str, str, str, result="QVariantMap")
    def updateContact(self, id_val: str, nombre: str, telefono: str, correo: str, ciudad: str) -> Dict[str, Any]:
        """Modifica in-place un contacto existente en disco."""
        payload = {
            "id": id_val,
            "nombre": nombre,
            "telefono": telefono,
            "correo": correo,
            "ciudad": ciudad
        }
        ok, msg, info = self._contact_service.update_contact(payload)
        if ok:
            self.loadContacts()
            self.verifyIntegrity()
            self.toastRequested.emit(msg, "success")
            return {"success": True, "message": msg, "info": info}
        else:
            self.toastRequested.emit(msg, "danger")
            return {"success": False, "message": msg, "info": {}}

    @Slot(str, result="QVariantMap")
    def deleteContact(self, id_val: str) -> Dict[str, Any]:
        """Elimina lógicamente un contacto (marca 'D' in-place)."""
        ok, msg = self._contact_service.delete_contact(id_val)
        if ok:
            self.loadContacts()
            self.verifyIntegrity()
            self.toastRequested.emit(msg, "success")
            return {"success": True, "message": msg}
        else:
            self.toastRequested.emit(msg, "danger")
            return {"success": False, "message": msg}

    @Slot(str, result="QVariantMap")
    def restoreContact(self, id_val: str) -> Dict[str, Any]:
        """Restaura un contacto de la papelera a estado activo."""
        ok, msg = self._contact_service.restore_contact(id_val)
        if ok:
            self.loadContacts()
            self.verifyIntegrity()
            self.toastRequested.emit(msg, "success")
            return {"success": True, "message": msg}
        else:
            self.toastRequested.emit(msg, "danger")
            return {"success": False, "message": msg}

    @Slot(str, result="QVariantMap")
    def getContactInspection(self, id_val: str) -> Dict[str, Any]:
        """Retorna los 256 bytes en formato hex y metadatos de seek() y tell()."""
        insp = self._contact_service.get_contact_inspection(id_val)
        if not insp:
            return {"success": False, "message": "Registro no encontrado"}
        return {"success": True, "data": insp}

    # ── Slots de Integridad y Diagnóstico ─────────────────────────────────────

    @Slot(result="QVariantMap")
    def verifyIntegrity(self) -> Dict[str, Any]:
        """Comprueba el sello SHA-256 de contactos.dat."""
        ok, stored, current, msg = self._contact_service.integrity_manager.verify()
        self._is_integrity_valid = ok
        self._stored_hash = stored
        self._calculated_hash = current
        self._system_status_msg = msg
        self.integrityChanged.emit()
        return {
            "isValid": ok,
            "storedHash": stored,
            "calculatedHash": current,
            "message": msg
        }

    @Slot(result="QVariantMap")
    def rebuildIndex(self) -> Dict[str, Any]:
        """Reconstruye indice.json escaneando secuencialmente el archivo .dat."""
        ok, msg, count = self._contact_service.rebuild_index()
        if ok:
            self.loadContacts()
            self.verifyIntegrity()
            self.toastRequested.emit(msg, "success")
            return {"success": True, "message": msg, "count": count}
        else:
            self.toastRequested.emit(msg, "danger")
            return {"success": False, "message": msg, "count": 0}

    @Slot(result="QVariantMap")
    def tamperDataForDemo(self) -> Dict[str, Any]:
        """
        Inyecta deliberadamente un byte 0xFF en el primer registro
        para demostrar cómo se rompe el sello SHA-256 ante manipulaciones externas.
        """
        if self._contact_service.record_manager.get_total_records() == 0:
            msg = "Debe haber al menos un contacto registrado para realizar la prueba."
            self.toastRequested.emit(msg, "warning")
            return {"success": False, "message": msg}

        self._contact_service.record_manager.tamper_byte(0, 15, 0xEE)
        self.verifyIntegrity()
        msg = "¡Demostración de laboratorio ejecutada! Se alteró un byte en disco. El sello SHA-256 ahora está ROTO."
        self.toastRequested.emit(msg, "danger")
        return {"success": True, "message": msg}

    @Slot(result="QVariantMap")
    def repairSeal(self) -> Dict[str, Any]:
        """Recalcula y vuelve a sellar el archivo con el hash actual."""
        new_hash = self._contact_service.integrity_manager.save_hash()
        self.verifyIntegrity()
        msg = f"Sello SHA-256 re-firmado exitosamente ({new_hash[:16]}...)."
        self.toastRequested.emit(msg, "success")
        return {"success": True, "message": msg, "newHash": new_hash}

    # ── Slots de Respaldos (Time Machine) ────────────────────────────────────

    @Slot(str, result="QVariantMap")
    def createBackup(self, note: str = "") -> Dict[str, Any]:
        """Crea un respaldo comprimido ZIP."""
        ok, msg, info = self._backup_service.create_backup(note)
        if ok:
            self.toastRequested.emit(msg, "success")
            return {"success": True, "message": msg, "info": info}
        else:
            self.toastRequested.emit(msg, "danger")
            return {"success": False, "message": msg, "info": {}}

    @Slot(result="QVariantList")
    def listBackups(self) -> List[Dict[str, Any]]:
        """Retorna el catálogo histórico de respaldos."""
        return self._backup_service.list_backups()

    @Slot(str, result="QVariantMap")
    def restoreBackup(self, filename: str) -> Dict[str, Any]:
        """Restaura un respaldo con Safe Restore previo."""
        ok, msg = self._backup_service.restore_backup(filename)
        if ok:
            self.loadContacts()
            self.verifyIntegrity()
            self.toastRequested.emit(msg, "success")
            return {"success": True, "message": msg}
        else:
            self.toastRequested.emit(msg, "danger")
            return {"success": False, "message": msg}

    # ── Slots de Exportación ─────────────────────────────────────────────────

    @Slot(result="QVariantMap")
    def exportToJson(self) -> Dict[str, Any]:
        ok, msg, path = self._export_service.export_json()
        if ok:
            self.toastRequested.emit(msg, "success")
            return {"success": True, "message": msg, "path": path}
        else:
            self.toastRequested.emit(msg, "danger")
            return {"success": False, "message": msg, "path": ""}

    @Slot(result="QVariantMap")
    def exportToCsv(self) -> Dict[str, Any]:
        ok, msg, path = self._export_service.export_csv()
        if ok:
            self.toastRequested.emit(msg, "success")
            return {"success": True, "message": msg, "path": path}
        else:
            self.toastRequested.emit(msg, "danger")
            return {"success": False, "message": msg, "path": ""}

    @Slot(result="QVariantMap")
    def exportToPdf(self) -> Dict[str, Any]:
        ok, msg, path = self._export_service.export_pdf()
        if ok:
            self.toastRequested.emit(msg, "success")
            return {"success": True, "message": msg, "path": path}
        else:
            self.toastRequested.emit(msg, "danger")
            return {"success": False, "message": msg, "path": ""}

    # ── Slots de Importación ─────────────────────────────────────────────────

    @Slot(str, result="QVariantMap")
    def previewCsv(self, filepath: str) -> Dict[str, Any]:
        clean_path = filepath.replace("file:///", "").replace("file://", "")
        ok, msg, info = self._import_service.preview_csv(clean_path)
        return {"success": ok, "message": msg, "data": info}

    @Slot(str, "QVariantMap", result="QVariantMap")
    def executeCsvImport(self, filepath: str, mapping: Dict[str, str]) -> Dict[str, Any]:
        clean_path = filepath.replace("file:///", "").replace("file://", "")
        ok, msg, summary = self._import_service.execute_import(clean_path, mapping)
        if ok:
            self.loadContacts()
            self.verifyIntegrity()
            self.toastRequested.emit(msg, "success")
            return {"success": True, "message": msg, "summary": summary}
        else:
            self.toastRequested.emit(msg, "danger")
            return {"success": False, "message": msg, "summary": {}}

    # ── Utilidades del Sistema y Sembrado ─────────────────────────────────────

    @Slot(int, result="QVariantMap")
    def seedDemoData(self, count: int = 10) -> Dict[str, Any]:
        """Inyecta contactos de demostración con nombres realistas en español y diacríticos."""
        demo_contacts = [
            ("101", "Ángel María Peña González", "+502 5555-1201", "angel.pena@empresa.com.gt", "Quetzaltenango"),
            ("102", "Valeria Sofía Méndez Cifuentes", "+502 5555-1202", "valeria.mendez@nexus.org", "Guatemala"),
            ("103", "Carlos René Rodas Alvarado", "+502 5555-1203", "carlos.rodas@corp.gt", "Antigua"),
            ("104", "Lucía Fernanda Morales Díaz", "+502 5555-1204", "lucia.morales@finanzas.com", "Quetzaltenango"),
            ("105", "Diego Alejandro Escobar López", "+502 5555-1205", "diego.escobar@tech.io", "Cobán"),
            ("106", "María José Gutiérrez Álvarez", "+502 5555-1206", "mj.gutierrez@innovacion.gt", "Guatemala"),
            ("107", "Fernando José Castillo Herrera", "+502 5555-1207", "fernando.castillo@legal.com", "Escuintla"),
            ("108", "Ana Gabriela Estrada Molina", "+502 5555-1208", "ana.estrada@salud.org", "Quetzaltenango"),
            ("109", "Héctor Manuel Pineda Vásquez", "+502 5555-1209", "hector.pineda@logistica.com", "Huehuetenango"),
            ("110", "Jimena Beatriz Arriola Cruz", "+502 5555-1210", "jimena.arriola@diseno.gt", "Guatemala"),
        ]

        inserted = 0
        for cid, nom, tel, mail, cd in demo_contacts[:count]:
            if not self._contact_service.index_manager.has(cid):
                ok, _, _ = self._contact_service.add_contact({
                    "id": cid, "nombre": nom, "telefono": tel, "correo": mail, "ciudad": cd
                })
                if ok:
                    inserted += 1

        self.loadContacts()
        self.verifyIntegrity()
        msg = f"Se insertaron {inserted} contactos de demostración en el archivo de 256 bytes."
        self.toastRequested.emit(msg, "info")
        return {"success": True, "message": msg, "inserted": inserted}

    @Slot(str)
    def setTheme(self, theme_name: str) -> None:
        self.set_current_theme(theme_name)

    @Slot(result="QVariantMap")
    def getSystemInfo(self) -> Dict[str, Any]:
        """Retorna información técnica del entorno y de los archivos de datos."""
        stats = self._contact_service.get_statistics()
        return {
            "appName": APP_NAME,
            "version": APP_VERSION,
            "organization": APP_ORGANIZATION,
            "pythonVersion": sys.version.split()[0],
            "recordSize": RECORD_SIZE,
            "dataFile": str(CONTACTS_FILE),
            "indexFile": str(INDEX_FILE),
            "hashFile": str(HASH_FILE),
            "totalRecords": stats["total_registros_fisicos"],
            "activeContacts": stats["total_activos"],
            "deletedContacts": stats["total_eliminados"],
            "fileSizeBytes": stats["tamano_archivo_bytes"]
        }

    @Slot(int, result="QVariantList")
    def getRecentLogs(self, limit: int = 50) -> List[str]:
        """Lee las últimas líneas del archivo app.log."""
        if not LOG_FILE.exists():
            return ["No hay registros en app.log aún."]
        try:
            with open(LOG_FILE, "r", encoding="utf-8", errors="replace") as f:
                lines = f.readlines()
            return [l.strip() for l in lines[-limit:]]
        except Exception as exc:
            return [f"Error leyendo logs: {exc}"]
