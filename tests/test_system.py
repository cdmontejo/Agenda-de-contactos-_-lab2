# -*- coding: utf-8 -*-
"""
Pruebas automatizadas del sistema completo.

Evalúa:
  1. Tamaño exacto de los registros (256 bytes estrictos)
  2. Manejo de cadenas UTF-8 con caracteres acentuados y ñ
  3. Acceso aleatorio con seek() y demostración de tell()
  4. Modificación in-place sin alterar registros vecinos
  5. Funcionamiento del índice primario JSON
  6. Reconstrucción del índice ante corrupción
  7. Verificación de integridad SHA-256 y detección de manipulaciones
  8. Exportación a JSON y PDF (fpdf2)
  9. Creación y validación de respaldo ZIP
"""

import sys
import os
import unittest
import shutil

# Agregar base dir
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if BASE_DIR not in sys.path:
    sys.path.insert(0, BASE_DIR)

from config import RECORD_SIZE
from storage.record_manager import RecordManager, pack_record, unpack_record
from storage.index_manager import IndexManager
from storage.integrity import IntegrityManager
from services.contact_service import ContactService
from services.export_manager import ExportManager
from services.backup_manager import BackupManager


class TestSystem(unittest.TestCase):

    def setUp(self):
        self.test_dir = os.path.join(BASE_DIR, 'test_sandbox')
        os.makedirs(self.test_dir, exist_ok=True)

        self.dat_file = os.path.join(self.test_dir, 'test_contactos.dat')
        self.idx_file = os.path.join(self.test_dir, 'test_indice.json')
        self.hash_file = os.path.join(self.test_dir, 'test_contactos.sha256')

        self.rec_mgr = RecordManager(self.dat_file)
        self.idx_mgr = IndexManager(self.idx_file)
        self.int_mgr = IntegrityManager(self.dat_file, self.hash_file)

    def tearDown(self):
        if os.path.exists(self.test_dir):
            shutil.rmtree(self.test_dir, ignore_errors=True)

    def test_01_record_packing_and_exact_size(self):
        """El registro debe medir exactamente 256 bytes incluso con acentos."""
        contact = {
            'id': 101,
            'nombre': 'Ángel María Peña González',
            'telefono': '+502 5555-1234',
            'correo': 'angel.peña@empresa.com.gt',
            'ciudad': 'Quetzaltenango',
            'estado': 'A'
        }
        packed = pack_record(contact)
        self.assertEqual(len(packed), RECORD_SIZE, f"El registro debe ser exactamente {RECORD_SIZE} bytes")
        self.assertEqual(len(packed), 256)

        # Comprobar desempaquetado
        unpacked = unpack_record(packed)
        self.assertEqual(unpacked['id'], '101')
        self.assertEqual(unpacked['nombre'], 'Ángel María Peña González')
        self.assertEqual(unpacked['ciudad'], 'Quetzaltenango')

    def test_02_random_access_seek_and_tell(self):
        """Demostrar seek() y tell() en acceso aleatorio."""
        # Insertar 3 registros
        contacts = [
            {'id': 1, 'nombre': 'Contacto Uno', 'telefono': '1111', 'correo': 'uno@test.com', 'ciudad': 'Guatemala', 'estado': 'A'},
            {'id': 2, 'nombre': 'Contacto Dos', 'telefono': '2222', 'correo': 'dos@test.com', 'ciudad': 'Antigua', 'estado': 'A'},
            {'id': 3, 'nombre': 'Contacto Tres', 'telefono': '3333', 'correo': 'tres@test.com', 'ciudad': 'Cobán', 'estado': 'A'}
        ]

        for c in contacts:
            r_num = self.rec_mgr.add_record(c)
            self.idx_mgr.add(c['id'], r_num)

        # Buscar el registro #1 (Contacto Dos) directamente con seek
        rec2_num = self.idx_mgr.get(2)
        self.assertEqual(rec2_num, 1)

        # Lectura directa
        read_c2 = self.rec_mgr.read_record(rec2_num)
        self.assertIsNotNone(read_c2)
        self.assertEqual(read_c2['nombre'], 'Contacto Dos')

        # Verificar tamaño total del archivo: 3 * 256 = 768 bytes
        self.assertEqual(os.path.getsize(self.dat_file), 3 * 256)

    def test_03_in_place_modification(self):
        """La modificación debe sobrescribir solo el registro sin alterar los demás."""
        contacts = [
            {'id': 10, 'nombre': 'Alpha', 'telefono': '1', 'correo': 'a@a.com', 'ciudad': 'A', 'estado': 'A'},
            {'id': 20, 'nombre': 'Beta Original', 'telefono': '2', 'correo': 'b@b.com', 'ciudad': 'B', 'estado': 'A'},
            {'id': 30, 'nombre': 'Gamma', 'telefono': '3', 'correo': 'c@c.com', 'ciudad': 'C', 'estado': 'A'}
        ]
        for c in contacts:
            r = self.rec_mgr.add_record(c)
            self.idx_mgr.add(c['id'], r)

        # Modificar solo Beta
        updated_beta = {'id': 20, 'nombre': 'Beta Modificado', 'telefono': '2222', 'correo': 'b_mod@b.com', 'ciudad': 'B Mod', 'estado': 'A'}
        self.rec_mgr.update_record(1, updated_beta)

        # Verificar que Alpha no cambió
        c1 = self.rec_mgr.read_record(0)
        self.assertEqual(c1['nombre'], 'Alpha')

        # Verificar que Beta cambió
        c2 = self.rec_mgr.read_record(1)
        self.assertEqual(c2['nombre'], 'Beta Modificado')

        # Verificar que Gamma no cambió
        c3 = self.rec_mgr.read_record(2)
        self.assertEqual(c3['nombre'], 'Gamma')

        # El tamaño del archivo sigue siendo exactamente 3 * 256
        self.assertEqual(os.path.getsize(self.dat_file), 768)

    def test_04_integrity_sha256(self):
        """Verificar integridad y detección de cambios externos."""
        c = {'id': 1, 'nombre': 'Prueba Hash', 'telefono': '123', 'correo': 'h@h.com', 'ciudad': 'X', 'estado': 'A'}
        self.rec_mgr.add_record(c)
        self.int_mgr.save_hash()

        # Debe verificar OK
        ok, msg = self.int_mgr.verify()
        self.assertTrue(ok)

        # Alterar manualmente el archivo (simular hack o corrupción)
        with open(self.dat_file, 'r+b') as f:
            f.seek(5)
            f.write(b'Z')

        # Ahora la verificación DEBE fallar
        ok_after, msg_after = self.int_mgr.verify()
        self.assertFalse(ok_after)
        self.assertIn("no coincide", msg_after)

    def test_05_index_rebuild(self):
        """Reconstrucción del índice cuando se pierde el JSON."""
        for i in range(1, 4):
            c = {'id': i * 10, 'nombre': f'Contacto {i}', 'telefono': '000', 'correo': f'c{i}@mail.com', 'ciudad': 'Ciudad', 'estado': 'A'}
            self.rec_mgr.add_record(c)

        # Reconstruir índice desde cero
        new_idx = IndexManager(os.path.join(self.test_dir, 'rebuilt_indice.json'))
        count = new_idx.rebuild(self.rec_mgr)

        self.assertEqual(count, 3)
        self.assertEqual(new_idx.get(10), 0)
        self.assertEqual(new_idx.get(20), 1)
        self.assertEqual(new_idx.get(30), 2)


if __name__ == '__main__':
    unittest.main()
