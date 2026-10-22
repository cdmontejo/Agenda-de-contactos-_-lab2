# -*- coding: utf-8 -*-
"""
Script de inicialización con datos de demostración empresarial.

Genera:
  - 12 contactos realistas con nombres y ciudades de Guatemala
  - Archivo contactos.dat (3,072 bytes exactos = 12 × 256)
  - Archivo indice.json primario
  - Archivo contactos.sha256 con hash criptográfico
  - Exportación en JSON (exports/contactos_export.json)
  - Reporte formal en PDF con fpdf2 (exports/reporte_contactos.pdf)
  - Respaldo comprimido ZIP (backups/respaldo_inicial.zip)
"""

import sys
import os

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
if BASE_DIR not in sys.path:
    sys.path.insert(0, BASE_DIR)

from services.contact_service import ContactService
from services.export_manager import ExportManager
from services.backup_manager import BackupManager


DEMO_CONTACTS = [
    {
        'id': 101,
        'nombre': 'Licda. María José Castillo Peña',
        'telefono': '+502 5521-8840',
        'correo': 'maria.castillo@corporacion.gt',
        'ciudad': 'Quetzaltenango'
    },
    {
        'id': 102,
        'nombre': 'Ing. Carlos Fernando Méndez Soto',
        'telefono': '+502 4410-2231',
        'correo': 'carlos.mendez@soluciones.com',
        'ciudad': 'Ciudad de Guatemala'
    },
    {
        'id': 103,
        'nombre': 'Dra. Sofía Alejandra Álvarez López',
        'telefono': '+502 5900-7762',
        'correo': 'sofia.alvarez@saludintegral.gt',
        'ciudad': 'Antigua Guatemala'
    },
    {
        'id': 104,
        'nombre': 'Arq. Roberto David Gómez Pineda',
        'telefono': '+502 3312-9901',
        'correo': 'roberto.gomez@urbanismo.gt',
        'ciudad': 'Escuintla'
    },
    {
        'id': 105,
        'nombre': 'Lic. Alejandro Morales Estrada',
        'telefono': '+502 5204-1189',
        'correo': 'alejandro.morales@finanzas.gt',
        'ciudad': 'Chimaltenango'
    },
    {
        'id': 106,
        'nombre': 'MSc. Claudia Beatriz Herrera Morales',
        'telefono': '+502 4118-4422',
        'correo': 'claudia.herrera@innovacion.edu',
        'ciudad': 'Cobán'
    },
    {
        'id': 107,
        'nombre': 'Ing. Diego Armando Rosales Paz',
        'telefono': '+502 5712-3344',
        'correo': 'diego.rosales@telecom.gt',
        'ciudad': 'Huehuetenango'
    },
    {
        'id': 108,
        'nombre': 'Valeria Stephanie Ruíz Quiñónez',
        'telefono': '+502 4901-5588',
        'correo': 'valeria.ruiz@marketing.gt',
        'ciudad': 'Mazatenango'
    },
    {
        'id': 109,
        'nombre': 'Lic. Gabriel Antonio Fuentes Lara',
        'telefono': '+502 3012-7711',
        'correo': 'gabriel.fuentes@auditoria.gt',
        'ciudad': 'Retalhuleu'
    },
    {
        'id': 110,
        'nombre': 'Inga. Andrea Jimena Paredes Cruz',
        'telefono': '+502 4620-8899',
        'correo': 'andrea.paredes@logistica.com',
        'ciudad': 'Puerto Barrios'
    },
    {
        'id': 111,
        'nombre': 'Lic. Héctor Manuel Salazar Ramos',
        'telefono': '+502 5811-2244',
        'correo': 'hector.salazar@comercio.gt',
        'ciudad': 'Quetzaltenango'
    },
    {
        'id': 112,
        'nombre': 'Licda. Lucía Mariana Velásquez Ortiz',
        'telefono': '+502 4209-6633',
        'correo': 'lucia.velasquez@consultores.gt',
        'ciudad': 'Sololá'
    }
]


def populate():
    print("Iniciando generación de datos de demostración...")
    service = ContactService()
    exporter = ExportManager(service)
    backuper = BackupManager(service)

    # Insertar contactos
    for contact in DEMO_CONTACTS:
        ok, msg = service.add_contact(contact)
        if ok:
            print(f"  ✓ {msg}")
        else:
            print(f"  ✕ {msg}")

    # Exportar JSON
    ok_j, msg_j, path_j = exporter.export_json()
    print(f"\n[Exportación JSON] {msg_j}\n  -> Archivo: {path_j}")

    # Exportar PDF
    ok_p, msg_p, path_p = exporter.export_pdf()
    print(f"\n[Exportación PDF] {msg_p}\n  -> Archivo: {path_p}")

    # Exportar CSV
    ok_c, msg_c, path_c = exporter.export_csv()
    print(f"\n[Exportación CSV] {msg_c}\n  -> Archivo: {path_c}")

    # Crear Respaldo ZIP
    ok_b, msg_b, info_b = backuper.create_backup()
    orig = info_b.get('original_size', 0)
    comp = info_b.get('compressed_size', 0)
    ratio = ((orig - comp) / orig * 100) if orig > 0 else 0
    print(f"\n[Respaldo ZIP] {msg_b}")
    print(f"  -> Archivo: {info_b.get('filepath')}")
    print(f"  -> Tamaño original: {orig} bytes | Comprimido: {comp} bytes (Reducción: {ratio:.1f}%)")

    # Verificar Integridad final
    ok_int, msg_int = service.verify_integrity()
    print(f"\n[Verificación de Integridad SHA-256] {msg_int} (Resultado: {ok_int})")


if __name__ == '__main__':
    try:
        sys.stdout.reconfigure(encoding='utf-8')
    except Exception:
        pass
    populate()
