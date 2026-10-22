# 📇 ContactManager Pro — Agenda de Contactos con Acceso Aleatorio

[![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/downloads/)
[![License: Academic](https://img.shields.io/badge/License-Academic-purple.svg)]()
[![Design: Liquid Glass](https://img.shields.io/badge/UI-Liquid%20Glass-8b5cf6.svg)]()

> **Laboratorio No. 2 — Estructuras de Datos Avanzadas y Manejo de Archivos**  
> *Facultad de Ingeniería en Informática y Sistemas — Universidad Rafael Landívar*  
> *Campus San Alberto Hurtado, S.J. de Quetzaltenango — Octubre 2026*

---

## 🌟 Resumen de Características Principales

ContactManager Pro es una aplicación de escritorio de nivel empresarial desarrollada en Python que administra una agenda de contactos sobre un **archivo de registros de tamaño fijo (256 bytes)** mediante **acceso aleatorio directo (`seek()` y `tell()`)** asistido por un **índice primario en JSON**.

### 💎 Diseño Visual Liquid Glass (Estilo iPhone / iOS)
- **Fondo animado fluido:** Blobs translúcidos en constante movimiento sinusoidal con desenfoque gaussiano suave mediante `PIL/Pillow`.
- **Efecto Glassmorphism:** Tarjetas, formularios y paneles oscuros (`#16162a`, `#1a1a32`) con bordes sutiles (`#2a2a4a`) y acentos púrpuras dinámicos (`#8b5cf6`).
- **Navegación tipo Sidebar:** Barra lateral ejecutiva con indicadores activos y transiciones al pasar el cursor.

---

## 📐 Estructura del Registro Fijo (256 Bytes)

Para garantizar que `offset = n * RECORD_SIZE` sea exacto en cualquier sistema operativo, los registros se miden en **bytes** con codificación **UTF-8**:

| Campo | Bytes | Descripción |
| :--- | :---: | :--- |
| `id` | **10** | Identificador entero único (alineado a la derecha con espacios) |
| `nombre` | **80** | Nombre completo (soporta tildes, diéresis y `ñ`) |
| `telefono` | **20** | Número telefónico nacional o internacional |
| `correo` | **80** | Dirección de correo electrónico |
| `ciudad` | **50** | Ciudad de residencia |
| `estado` | **1** | `'A'` = Activo, `'D'` = Eliminado lógicamente |
| `padding` | **14** | Relleno (`0x20`) para alineación binaria uniforme |
| `newline` | **1** | `\n` (`0x0A`) para legibilidad e inspección limpia |
| **TOTAL** | **256** | **Tamaño estricto por contacto en `contactos.dat`** |

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

1. **Búsqueda por ID:** No recorre el archivo completo ($O(1)$ amortizado). Consulta el índice primario en RAM y ejecuta `f.seek(record_num * 256)`.
2. **Demostración de `tell()`:** En la barra de estado y en los logs se reporta la posición exacta en bytes antes y después de cada I/O.
3. **Modificación in-place:** Al editar un contacto solo se sobrescribe su bloque de 256 bytes en el disco con `r+b`. El resto del archivo permanece intacto.
4. **Eliminación lógica:** El registro se marca con `'D'` en su byte de estado. Puede restaurarse en cualquier momento.

---

## 🛡️ Seguridad, Integridad y Respaldos

- **Verificación Criptográfica SHA-256:** Cada guardado calcula el hash del archivo `contactos.dat` y lo guarda en `contactos.sha256`. Al arrancar la aplicación, se recalcula y compara; si no coincide, alerta al usuario sobre alteraciones externas.
- **Respaldos ZIP con DEFLATE:** Empaqueta `contactos.dat`, `indice.json` y `contactos.sha256` en un archivo `.zip`. Muestra el tamaño original frente al comprimido (ahorro típico del **62%**).
- **Restauración Asistida:** Permite restaurar desde cualquier ZIP previo, generando automáticamente un respaldo de seguridad del estado actual.
- **Reconstrucción del Índice:** Si `indice.json` se corrompe o borra, la aplicación lo regenera escaneando los 256 bytes de cada registro.

---

## 🚀 Requisitos e Instalación

### 1. Clonar o descargar el repositorio
```bash
git clone <url-del-repositorio>
cd Agenda-de-contactos-_-lab2
```

### 2. Instalar dependencias
```bash
pip install -r requirements.txt
```
*(Requiere `fpdf2` y `Pillow`. `tkinter` viene incluido con la instalación estándar de Python).*

### 3. Poblar datos iniciales de demostración (Opcional)
```bash
python seed_demo_data.py
```

### 4. Ejecutar la aplicación
```bash
python main.py
```

### 5. Ejecutar pruebas automatizadas
```bash
python -m unittest tests/test_system.py
```

---

## ⌨️ Atajos de Teclado

| Atajo | Función |
| :--- | :--- |
| `Ctrl + N` | Registrar nuevo contacto |
| `Ctrl + F` | Búsqueda directa por ID con demostración de `seek()` |
| `Ctrl + E` | Exportar todos los contactos a JSON |
| `Ctrl + B` | Crear respaldo comprimido ZIP |
| `F5` | Refrescar registros, métricas y estadísticas |

---

## 📁 Estructura del Código

```
Agenda-de-contactos-_-lab2/
├── config.py                  # Constantes, tamaños binarios y rutas
├── main.py                    # Punto de entrada de la aplicación
├── seed_demo_data.py          # Generador de datos y entregables
├── generate_report_pdf.py     # Compilador de la documentación técnica
├── requirements.txt           # Dependencias oficiales
│
├── storage/                   # Capa de almacenamiento y bajo nivel
│   ├── record_manager.py      # Registros fijos 256B + seek() y tell()
│   ├── index_manager.py       # Índice primario JSON (ID -> registro)
│   └── integrity.py           # Cálculo y verificación SHA-256
│
├── services/                  # Lógica de negocio y servicios
│   ├── contact_service.py     # Orquestador CRUD y filtros
│   ├── export_manager.py      # Exportación a JSON, PDF y CSV
│   ├── backup_manager.py      # Respaldos ZIP y restauración
│   └── validators.py          # Validación de campos y longitudes
│
├── ui/                        # Interfaz gráfica Liquid Glass
│   ├── app.py                 # Ventana principal, navegación y menú
│   ├── animated_bg.py         # Canvas con fondo animado sinusoidal
│   ├── theme.py               # Tokens visuales, colores y tipografía
│   ├── components.py          # Tarjetas, botones, buscador y tablas
│   ├── dialogs.py             # Diálogos modales, stat/access, ZIP info
│   ├── contact_form.py        # Formulario reactivo de alta y edición
│   ├── dashboard_view.py      # Panel ejecutivo con indicadores
│   ├── contacts_view.py       # Directorio de contactos con filtros
│   ├── export_view.py         # Módulo de exportación con historial
│   ├── tools_view.py          # Herramientas de integridad y mantenimiento
│   └── help_view.py           # Documentación y atajos
│
├── data/                      # Archivos de datos generados
│   ├── contactos.dat          # Registros fijos (3,072 bytes)
│   ├── indice.json            # Mapeo clave-registro
│   └── contactos.sha256       # Hash SHA-256 de integridad
│
├── exports/                   # Archivos exportados (JSON, PDF, CSV)
├── backups/                   # Respaldos comprimidos ZIP
├── tests/                     # Suite de pruebas unitarias
└── docs/                      # Documento técnico obligatorio en PDF y MD
```

