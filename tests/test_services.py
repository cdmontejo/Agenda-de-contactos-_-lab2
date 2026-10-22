# -*- coding: utf-8 -*-
"""
Pruebas automatizadas de la capa de servicios (ContactService, BackupService, ExportService).
"""

import sys
import shutil
import tempfile
import unittest
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
if str(BASE_DIR) not in sys.path:
    sys.path.insert(0, str(BASE_DIR))

from src.services.contact_service import ContactService
from src.services.backup_service import BackupService
from src.services.export_service import ExportService


class TestServices(unittest.TestCase):

    def setUp(self):
        self.test_dir = Path(tempfile.mkdtemp(prefix="test_hub_services_"))
        self.dat_file = self.test_dir / "contactos.dat"
        self.idx_file = self.test_dir / "indice.json"
        self.sha_file = self.test_dir / "contactos.sha256"
        self.backup_dir = self.test_dir / "backups"
        self.export_dir = self.test_dir / "exports"

        self.contact_service = ContactService(
            data_file=self.dat_file,
            index_file=self.idx_file,
            hash_file=self.sha_file
        )
        self.backup_service = BackupService(
            contact_service=self.contact_service,
            backups_dir=self.backup_dir
        )
        self.export_service = ExportService(
            contact_service=self.contact_service,
            exports_dir=self.export_dir
        )

    def tearDown(self):
        if self.test_dir.exists():
            shutil.rmtree(self.test_dir, ignore_errors=True)

    def test_01_crud_operations(self):
        """Verifica ciclo de vida completo: inserción, lectura, actualización y eliminación lógica."""
        contact = {
            "id": 101,
            "nombre": "Valeria Méndez",
            "telefono": "+502 5555-0001",
            "correo": "valeria@test.com",
            "ciudad": "Guatemala"
        }

        # 1. Crear
        ok, msg, info = self.contact_service.add_contact(contact)
        self.assertTrue(ok)
        self.assertEqual(info["record_num"], 0)
        self.assertEqual(info["byte_offset"], 0)

        # 2. Consultar
        ok_get, _, c_read = self.contact_service.get_contact_by_id(101)
        self.assertTrue(ok_get)
        self.assertEqual(c_read["nombre"], "Valeria Méndez")

        # 3. Actualizar in-place
        contact["nombre"] = "Valeria Sofía Méndez"
        ok_up, _, _ = self.contact_service.update_contact(contact)
        self.assertTrue(ok_up)

        _, _, c_after_up = self.contact_service.get_contact_by_id(101)
        self.assertEqual(c_after_up["nombre"], "Valeria Sofía Méndez")

        # 4. Eliminación lógica ('A' -> 'D')
        ok_del, _ = self.contact_service.delete_contact(101)
        self.assertTrue(ok_del)

        # Ya no debe estar en índice activo
        ok_after_del, _, _ = self.contact_service.get_contact_by_id(101)
        self.assertFalse(ok_after_del)

        # 5. Restauración
        ok_res, _ = self.contact_service.restore_contact(101)
        self.assertTrue(ok_res)
        ok_after_res, _, _ = self.contact_service.get_contact_by_id(101)
        self.assertTrue(ok_after_res)

    def test_02_backup_and_restore(self):
        """Creación de respaldo ZIP con DEFLATE y protocolo Safe Restore."""
        self.contact_service.add_contact({
            "id": 1,
            "nombre": "Contacto Backup",
            "telefono": "+502 1234",
            "correo": "b@test.com",
            "ciudad": "Antigua"
        })

        # Crear respaldo
        ok_b, msg_b, info_b = self.backup_service.create_backup(note="Test Backup")
        self.assertTrue(ok_b)
        self.assertTrue(Path(info_b["filepath"]).exists())

        backups = self.backup_service.list_backups()
        self.assertGreaterEqual(len(backups), 1)

        # Restaurar
        ok_r, msg_r = self.backup_service.restore_backup(info_b["filename"])
        self.assertTrue(ok_r)

    def test_03_exports_json_csv_pdf(self):
        """Exportación a JSON, CSV con BOM y PDF corporativo."""
        self.contact_service.add_contact({
            "id": 201,
            "nombre": "Ángel Peña",
            "telefono": "+502 4444",
            "correo": "angel@peña.gt",
            "ciudad": "Quetzaltenango"
        })

        # JSON
        ok_j, _, path_j = self.export_service.export_json()
        self.assertTrue(ok_j)
        self.assertTrue(Path(path_j).exists())

        # CSV
        ok_c, _, path_c = self.export_service.export_csv()
        self.assertTrue(ok_c)
        self.assertTrue(Path(path_c).exists())

        # PDF con fpdf2
        ok_p, _, path_p = self.export_service.export_pdf()
        self.assertTrue(ok_p)
        self.assertTrue(Path(path_p).exists())
        self.assertGreater(Path(path_p).stat().st_size, 1000)


if __name__ == "__main__":
    unittest.main()
