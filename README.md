# 📇 ContactHub Enterprise v2.0

[![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/downloads/)
[![Framework: PySide6 / QML](https://img.shields.io/badge/GUI-PySide6%20%7C%20Qt%20Quick%20QML-41cd52.svg)](https://www.qt.io/)
[![Persistence: Fixed 256B Records](https://img.shields.io/badge/Storage-Fixed%20256B%20Binary-8b5cf6.svg)]()
[![Security: SHA--256](https://img.shields.io/badge/Security-SHA--256%20FIPS%20180--4-10b981.svg)]()
[![License: Academic](https://img.shields.io/badge/License-Academic%20URL-orange.svg)]()

> **Laboratorio No. 2 — Estructuras de Datos Avanzadas y Manejo de Archivos**  
> *Facultad de Ingeniería en Informática y Sistemas — Universidad Rafael Landívar*  
> *Campus San Alberto Hurtado, S.J. de Quetzaltenango — Octubre 2026*

---

## 🌟 Visión General

**ContactHub Enterprise** es una plataforma de escritorio de alto rendimiento para la gestión corporativa de contactos. Combina una arquitectura de bajo nivel basada en **registros de tamaño fijo (256 bytes estrictos)** con **acceso aleatorio directo (`seek()` y `tell()`)**, asistido por un **índice primario en JSON** ($O(1)$) y **verificación criptográfica SHA-256**, todo presentado a través de una interfaz moderna y fluida desarrollada con **PySide6 y Qt Quick/QML**.

---

## 📐 Especificación del Registro Inmutable (256 Bytes)

Para garantizar que `offset = n * RECORD_SIZE` sea exacto en cualquier sistema operativo, los registros se miden en **bytes** reales en codificación **UTF-8**:

```
0        10                  90          110                 190                240 241           255 256
┌────────┬───────────────────┬───────────┬───────────────────┬──────────────────┬───┬─────────────┬───┐
│ ID     │ Nombre            │ Teléfono  │ Correo            │ Ciudad           │Est│ Padding     │\n │
│ 10 B   │ 80 B              │ 20 B      │ 80 B              │ 50 B             │1B │ 14 B        │1B │
└────────┴───────────────────┴───────────┴───────────────────┴──────────────────┴───┴─────────────┴───┘
```

| Campo | Bytes | Codificación | Relleno / Alineación | Descripción |
| :--- | :---: | :---: | :---: | :--- |
| `id` | **10** | UTF-8 | Relleno a la izquierda con espacios | Identificador numérico único ($\le 9,999,999,999$) |
| `nombre` | **80** | UTF-8 | Relleno a la derecha (`0x20`) | Nombre completo (soporta tildes, eñes y diéresis) |
| `telefono` | **20** | UTF-8 | Relleno a la derecha (`0x20`) | Número telefónico con prefijos y formato |
| `correo` | **80** | UTF-8 | Relleno a la derecha (`0x20`) | Dirección de correo electrónico |
| `ciudad` | **50** | UTF-8 | Relleno a la derecha (`0x20`) | Ciudad de residencia |
| `estado` | **1** | ASCII | Byte único | `'A'` = Activo, `'D'` = Eliminado lógicamente |
| `padding` | **14** | Binario | Espacios (`0x20`) | Alineación binaria para expansión de versión |
| `newline` | **1** | ASCII | `\n` (`0x0A`) | Delimitador para visualización limpia en hex |
| **TOTAL** | **256** | — | — | **Tamaño estricto e invariable por registro** |

---

## ⚡ Rigor Técnico del Acceso Aleatorio

```
Índice en RAM (indice.json)         Archivo en Disco (contactos.dat)
┌──────────────┐                    ┌───────────────────────────────┐
│ ID: 106      │ ──[ O(1) ]──>      │ Registro #5                   │
│ Registro: 5  │                    │ Offset: 5 × 256 = 1280 bytes  │
└──────────────┘                    │ seek(1280) -> tell() = 1280B  │
                                    └───────────────────────────────┘
```

1. **Búsqueda por ID en $O(1)$:** Consulta el índice primario en RAM (`indice.json`) y ejecuta `f.seek(record_num * 256, os.SEEK_SET)`.
2. **Demostración de `tell()`:** La interfaz gráfica muestra en tiempo real el puntero devuelto por `f.tell()` antes y después de cada operación.
3. **Modificación In-Place:** Al editar un contacto solo se sobrescribe su bloque de 256 bytes en el disco con `r+b`. El tamaño total del archivo no varía ni un solo byte.
4. **Eliminación Lógica:** El registro se marca con `'D'` en su byte de estado. Puede restaurarse a `'A'` en cualquier momento.
5. **Inspección Hexadecimal:** Modal interactivo que muestra los 256 bytes exactos en hexadecimal y ASCII.

---

## 🛡️ Seguridad e Integridad Criptográfica

- **Sello SHA-256 (FIPS 180-4):** Cada operación atómica calcula el digest de `contactos.dat` en bloques de 8192 bytes y lo persiste en `contactos.sha256`.
- **Detección de Tampering:** Si el archivo se modifica externamente (incluso un solo bit), el sistema detecta la rotura del sello por efecto avalancha.
- **Time Machine de Respaldos:** Generación de copias `.zip` con compresión DEFLATE (~60% de reducción). Incluye protocolo *Safe Restore* con snapshot preventivo.
- **Reconstrucción del Índice:** Si `indice.json` se elimina o corrompe, el sistema escanea los 256 bytes de cada registro y lo regenera automáticamente.

---

## 🚀 Instalación y Ejecución

### 1. Requisitos
- Python 3.10+
- PySide6 6.5+
- fpdf2 2.7+

### 2. Instalar dependencias
```bash
pip install -r requirements.txt
```

### 3. Poblar datos iniciales de prueba (Opcional)
```bash
python seed_demo_data.py
```

### 4. Iniciar la aplicación
```bash
python main.py
```

### 5. Ejecutar la suite de pruebas
```bash
python -m unittest discover tests
```
