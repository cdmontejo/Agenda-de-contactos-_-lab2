# -*- coding: utf-8 -*-
"""
Script utilitario de población de datos iniciales para ContactHub Enterprise.
Genera contactos con nombres hispanos realistas, tildes, eñes y números telefónicos
válidos para demostrar el empaquetado exacto de 256 bytes y la búsqueda O(1).
"""

import sys
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent
if str(BASE_DIR) not in sys.path:
    sys.path.insert(0, str(BASE_DIR))

from src.services.contact_service import ContactService

DEMO_CONTACTS = [
    {
        "id": 101,
        "nombre": "Ángel María Peña González",
        "telefono": "+502 5555-1201",
        "correo": "angel.pena@corporacion.gt",
        "ciudad": "Quetzaltenango"
    },
    {
        "id": 102,
        "nombre": "Valeria Sofía Méndez Cifuentes",
        "telefono": "+502 5555-1202",
        "correo": "valeria.mendez@consultoria.org",
        "ciudad": "Guatemala"
    },
    {
        "id": 103,
        "nombre": "Carlos René Rodas Alvarado",
        "telefono": "+502 5555-1203",
        "correo": "carlos.rodas@tecnologia.gt",
        "ciudad": "Antigua Guatemala"
    },
    {
        "id": 104,
        "nombre": "Lucía Fernanda Morales Díaz",
        "telefono": "+502 5555-1204",
        "correo": "lucia.morales@finanzas.com",
        "ciudad": "Quetzaltenango"
    },
    {
        "id": 105,
        "nombre": "Diego Alejandro Escobar López",
        "telefono": "+502 5555-1205",
        "correo": "diego.escobar@servicios.io",
        "ciudad": "Cobán"
    },
    {
        "id": 106,
        "nombre": "María José Gutiérrez Álvarez",
        "telefono": "+502 5555-1206",
        "correo": "mj.gutierrez@innovacion.gt",
        "ciudad": "Guatemala"
    },
    {
        "id": 107,
        "nombre": "Fernando José Castillo Herrera",
        "telefono": "+502 5555-1207",
        "correo": "fernando.castillo@legal.com",
        "ciudad": "Escuintla"
    },
    {
        "id": 108,
        "nombre": "Ana Gabriela Estrada Molina",
        "telefono": "+502 5555-1208",
        "correo": "ana.estrada@salud.org",
        "ciudad": "Quetzaltenango"
    },
    {
        "id": 109,
        "nombre": "Héctor Manuel Pineda Vásquez",
        "telefono": "+502 5555-1209",
        "correo": "hector.pineda@logistica.com",
        "ciudad": "Huehuetenango"
    },
    {
        "id": 110,
        "nombre": "Jimena Beatriz Arriola Cruz",
        "telefono": "+502 5555-1210",
        "correo": "jimena.arriola@diseno.gt",
        "ciudad": "Guatemala"
    }
]


def seed():
    service = ContactService()
    print("=" * 60)
    print("Iniciando sembrado de datos en ContactHub Enterprise...")
    print("=" * 60)

    inserted = 0
    for c in DEMO_CONTACTS:
        cid = str(c["id"])
        if service.index_manager.has(cid):
            print(f"[-] ID {cid} ya existe en el índice. Omitido.")
            continue

        ok, msg, info = service.add_contact(c)
        if ok:
            inserted += 1
            print(f"[+] Registrado #{info['record_num']} (Offset: {info['byte_offset']}B): {c['nombre']}")
        else:
            print(f"[x] Error en ID {cid}: {msg}")

    print("-" * 60)
    print(f"Sembrado finalizado: {inserted} contactos insertados.")
    print(f"Registros en disco: {service.record_manager.get_total_records()}")
    print(f"Hash SHA-256: {service.integrity_manager.get_stored_hash()}")
    print("=" * 60)


if __name__ == "__main__":
    seed()

