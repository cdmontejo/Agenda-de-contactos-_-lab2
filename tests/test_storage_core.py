# -*- coding: utf-8 -*-
"""
Pruebas rigurosas de bajo nivel para el motor de persistencia binaria de 256 bytes,
acceso aleatorio O(1) con seek() y tell(), e integridad criptográfica SHA-256.
"""

import sys
import shutil
import tempfile
import unittest
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
if str(BASE_DIR) not in sys.path:
    sys.path.insert(0, str(BASE_DIR))

from config import RECORD_SIZE
from src.storage.record_manager import (
    RecordManager,
    pack_field,
    unpack_field,
    pack_record,
    unpack_record
)
from src.storage.index_manager import IndexManager
from src.storage.integrity_manager import IntegrityManager


class TestStorageCore(unittest.TestCase):

    def setUp(self):
        self.test_dir = Path(tempfile.mkdtemp(prefix="test_hub_storage_"))
        self.dat_file = self.test_dir / "contactos.dat"
        self.idx_file = self.test_dir / "indice.json"
        self.sha_file = self.test_dir / "contactos.sha256"

        self.record_mgr = RecordManager(self.dat_file)
        self.index_mgr = IndexManager(self.idx_file)
        self.integrity_mgr = IntegrityManager(self.dat_file, self.sha_file)

    def tearDown(self):
        if self.test_dir.exists():
            shutil.rmtree(self.test_dir, ignore_errors=True)

    def test_01_pack_field_utf8_accents_and_exact_size(self):
        """pack_field debe ajustar con precisión los bytes y respetar secuencias multibyte."""
        nombre_con_tildes = "Ángel María Peña González"
        packed = pack_field(nombre_con_tildes, 80)
        self.assertEqual(len(packed), 80, "El campo debe medir exactamente 80 bytes.")

        # Desempaquetado limpio sin espacios de relleno
        unpacked = unpack_field(packed)
        self.assertEqual(unpacked, nombre_con_tildes)

    def test_02_record_packing_strictly_256_bytes(self):
        """El registro debe medir exactamente 256 bytes en cualquier circunstancia."""
        contact = {
            "id": 101,
            "nombre": "Ángel María Peña González",
            "telefono": "+502 5555-1201",
            "correo": "angel.pena@empresa.com.gt",
            "ciudad": "Quetzaltenango",
            "estado": "A"
        }
        packed = pack_record(contact)
        self.assertEqual(len(packed), RECORD_SIZE)
        self.assertEqual(len(packed), 256)
        self.assertEqual(packed[-1:], b"\n")  # El último byte debe ser \n

        unpacked = unpack_record(packed)
        self.assertIsNotNone(unpacked)
        self.assertEqual(unpacked["id"], 101)
        self.assertEqual(unpacked["nombre"], "Ángel María Peña González")
        self.assertEqual(unpacked["ciudad"], "Quetzaltenango")
        self.assertEqual(unpacked["estado"], "A")

    def test_03_random_access_seek_and_tell(self):
        """Demostración matemática de acceso aleatorio directo O(1) con seek() y tell()."""
        contacts = [
            {"id": 1, "nombre": "Contacto Uno", "telefono": "1111", "correo": "u@test.com", "ciudad": "Guate"},
            {"id": 2, "nombre": "Contacto Dos", "telefono": "2222", "correo": "d@test.com", "ciudad": "Antigua"},
            {"id": 3, "nombre": "Contacto Tres", "telefono": "3333", "correo": "t@test.com", "ciudad": "Cobán"},
        ]

        for c in contacts:
            rec_num, p_ini, p_fin = self.record_mgr.add_record(c)
            self.index_mgr.add(c["id"], rec_num)

        # Acceso directo al contacto #2 (ID 2, record_num = 1)
        rec2_num = self.index_mgr.get(2)
        self.assertEqual(rec2_num, 1)

        c2, tell_antes, tell_despues = self.record_mgr.read_record(rec2_num)
        self.assertEqual(c2["nombre"], "Contacto Dos")
        self.assertEqual(tell_antes, 1 * RECORD_SIZE)      # 256 bytes
        self.assertEqual(tell_despues, 2 * RECORD_SIZE)    # 512 bytes

    def test_04_in_place_update_without_shifting_neighbors(self):
        """Modificar in-place en disco no debe alterar el tamaño ni los registros vecinos."""
        c1 = {"id": 1, "nombre": "Original Uno", "telefono": "111", "correo": "1@a.com", "ciudad": "C1"}
        c2 = {"id": 2, "nombre": "Original Dos", "telefono": "222", "correo": "2@a.com", "ciudad": "C2"}
        c3 = {"id": 3, "nombre": "Original Tres", "telefono": "333", "correo": "3@a.com", "ciudad": "C3"}

        r1, _, _ = self.record_mgr.add_record(c1)
        r2, _, _ = self.record_mgr.add_record(c2)
        r3, _, _ = self.record_mgr.add_record(c3)

        initial_size = self.dat_file.stat().st_size
        self.assertEqual(initial_size, 3 * 256)

        # Modificar in-place el registro #2 (Contacto Dos)
        c2_updated = {"id": 2, "nombre": "Dos Modificado In-Place", "telefono": "+502 9999", "correo": "new@a.com", "ciudad": "Xela"}
        self.record_mgr.update_record(r2, c2_updated)

        # El tamaño del archivo debe seguir siendo exactamente 3 * 256
        self.assertEqual(self.dat_file.stat().st_size, initial_size)

        # Verificar que el registro 1 y 3 permanecen intactos
        read_c1, _, _ = self.record_mgr.read_record(r1)
        read_c3, _, _ = self.record_mgr.read_record(r3)
        self.assertEqual(read_c1["nombre"], "Original Uno")
        self.assertEqual(read_c3["nombre"], "Original Tres")

        # Verificar que el registro 2 se actualizó
        read_c2, _, _ = self.record_mgr.read_record(r2)
        self.assertEqual(read_c2["nombre"], "Dos Modificado In-Place")

    def test_05_index_rebuild_from_binary_file(self):
        """El índice JSON debe poder reconstruirse totalmente si se borra o corrompe."""
        for i in range(5):
            c = {"id": 100 + i, "nombre": f"Contacto {i}", "telefono": "123", "correo": "a@b.com", "ciudad": "Guate"}
            self.record_mgr.add_record(c)

        # Simular borrado de indice.json
        if self.idx_file.exists():
            self.idx_file.unlink()

        # Reconstruir índice escaneando el archivo físico
        all_records = self.record_mgr.read_all_records(include_deleted=True)
        count = self.index_mgr.rebuild(all_records)
        self.assertEqual(count, 5)
        self.assertEqual(self.index_mgr.get(103), 3)

    def test_06_sha256_integrity_and_tampering_detection(self):
        """La verificación SHA-256 debe detectar alteraciones externas bit a bit."""
        c = {"id": 1, "nombre": "Contacto Fiel", "telefono": "123", "correo": "f@f.com", "ciudad": "Guate"}
        self.record_mgr.add_record(c)
        saved_hash = self.integrity_mgr.save_hash()

        # Verificación inicial: debe ser 100% válida
        ok, stored, current, msg = self.integrity_mgr.verify()
        self.assertTrue(ok)
        self.assertEqual(stored, current)

        # Simular alteración externa (tampering de un byte)
        self.record_mgr.tamper_byte(0, 10, 0x58)  # Cambia un byte en el offset 10

        # Verificación posterior: el sello debe estar ROTO
        ok_after, stored_after, current_after, msg_after = self.integrity_mgr.verify()
        self.assertFalse(ok_after)
        self.assertNotEqual(stored_after, current_after)
        self.assertIn("ROTO", msg_after)


if __name__ == "__main__":
    unittest.main()
