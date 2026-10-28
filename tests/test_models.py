# -*- coding: utf-8 -*-
"""
Pruebas de modelos Qt (ContactListModel) y controladores MVVM (AppController).
"""

import sys
import unittest
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
if str(BASE_DIR) not in sys.path:
    sys.path.insert(0, str(BASE_DIR))

from PySide6.QtWidgets import QApplication
from PySide6.QtCore import Qt

from src.viewmodels.contact_model import ContactListModel
from src.viewmodels.app_controller import AppController

# Crear o reutilizar QApplication para testing de QObject
app = QApplication.instance() or QApplication(sys.argv)


class TestModels(unittest.TestCase):

    def setUp(self):
        self.model = ContactListModel()
        self.controller = AppController()

    def test_01_contact_list_model_roles_and_virtualization(self):
        """Verifica roles del modelo reactivo Qt."""
        contacts = [
            {"id": 1, "nombre": "Ana Pérez", "telefono": "111", "correo": "a@p.com", "ciudad": "Guate", "estado": "A", "byte_offset": 0, "record_num": 0},
            {"id": 2, "nombre": "Beto Díaz", "telefono": "222", "correo": "b@d.com", "ciudad": "Xela", "estado": "D", "byte_offset": 256, "record_num": 1}
        ]
        self.model.set_contacts(contacts)
        self.assertEqual(self.model.rowCount(), 2)

        idx0 = self.model.index(0, 0)
        self.assertEqual(self.model.data(idx0, self.model.IdRole), 1)
        self.assertEqual(self.model.data(idx0, self.model.NombreRole), "Ana Pérez")
        self.assertEqual(self.model.data(idx0, self.model.OffsetRole), 0)

        idx1 = self.model.index(1, 0)
        self.assertEqual(self.model.data(idx1, self.model.EstadoRole), "D")
        self.assertEqual(self.model.data(idx1, self.model.OffsetRole), 256)

    def test_02_app_controller_properties_and_theme(self):
        """Verifica propiedades reactivas y cambio de tema."""
        current_theme = self.controller.currentTheme
        self.assertIn(current_theme, ["dark", "light"])

        # Cambiar tema
        self.controller.setTheme("light")
        self.assertEqual(self.controller.currentTheme, "light")

        self.controller.setTheme("dark")
        self.assertEqual(self.controller.currentTheme, "dark")


if __name__ == "__main__":
    unittest.main()

