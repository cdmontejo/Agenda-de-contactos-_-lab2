# 📑 INFORME TÉCNICO Y MEMORIA DE ARQUITECTURA
## Laboratorio No. 2: Agenda de Contactos con Acceso Aleatorio e Indexación Primaria
**Universidad Rafael Landívar — Campus San Alberto Hurtado, S.J. de Quetzaltenango**  
**Facultad de Ingeniería en Informática y Sistemas**  
**Octubre 2026**

---

## 1. Estructura del Registro Fijo (256 Bytes)

Para garantizar un acceso aleatorio exacto mediante la fórmula `offset = n * RECORD_SIZE`, todos los registros en `contactos.dat` tienen una longitud binaria estrictamente uniforme de **256 bytes**.

### Tabla de Campos y Tamaños en Bytes
| Campo | Tipo / Formato | Tamaño en Bytes | Estrategia de Relleno y Codificación |
| :--- | :--- | :---: | :--- |
| **ID** | Entero único | **10 B** | Numérico alineado a la derecha con espacios (`0x20`) |
| **Nombre** | Cadena UTF-8 | **80 B** | UTF-8, soporte para tildes y caracteres hispanos, `ljust(80, b' ')` |
| **Teléfono** | Cadena UTF-8 | **20 B** | Formato nacional/internacional, `ljust(20, b' ')` |
| **Correo** | Cadena UTF-8 | **80 B** | Formato RFC simplificado, `ljust(80, b' ')` |
| **Ciudad** | Cadena UTF-8 | **50 B** | Texto UTF-8, `ljust(50, b' ')` |
| **Estado** | Carácter (1 byte) | **1 B** | `'A'` = Activo, `'D'` = Eliminado Lógicamente |
| **Padding** | Bytes neutros | **14 B** | Relleno (`0x20`) para alineación binaria de 256 bytes |
| **Salto de Línea** | Separador `\n` | **1 B** | `0x0A` (`\n`) para inspección legible sin romper la longitud |
| **TOTAL** | **Registro Fijo** | **256 Bytes** | **Exacto e invariable en todo el archivo** |

### Manejo de UTF-8 y Caracteres Multibyte
En Python, caracteres como `'á'` o `'ñ'` consumen 2 bytes en UTF-8. Para evitar desplazamientos espurios en el cálculo de `seek()`:
1. Las longitudes se delimitan en **bytes**, nunca en número de caracteres.
2. La función `pack_field()` codifica a UTF-8 y recorta caracter por caracter solo si la representación binaria excede la cuota del campo, evitando mutilar bytes internos de caracteres multibyte.
3. Se aplica relleno binario con espacios (`b' '`).

---

## 2. Implementación de Acceso Aleatorio con `seek()` y `tell()`

El acceso aleatorio permite leer o modificar cualquier registro en tiempo constante $O(1)$ sin recorrer secuencialmente el archivo.

### Cálculo de Posición (Offset)
$$\text{Offset en Bytes} = \text{Número de Registro} \times 256$$

### Fragmento de Código: Lectura Directa
```python
def read_record(self, record_num: int) -> dict | None:
    offset = record_num * RECORD_SIZE
    with open(self.filepath, 'rb') as f:
        # 1. Posicionamiento directo en el disco
        f.seek(offset)
        pos_before = f.tell()  # Demostración tell()
        
        # 2. Lectura exacta de 256 bytes
        data = f.read(RECORD_SIZE)
        pos_after = f.tell()
        
        logger.info("seek(%d) -> tell() antes: %dB, tell() después: %dB", 
                    offset, pos_before, pos_after)
        
        if len(data) < RECORD_SIZE:
            return None
        return unpack_record(data)
```

### Fragmento de Código: Modificación In-Place
```python
def update_record(self, record_num: int, contact: dict):
    offset = record_num * RECORD_SIZE
    data = pack_record(contact)  # Exactamente 256 bytes
    
    with open(self.filepath, 'r+b') as f:
        # Se traslada el puntero directamente al registro a editar
        f.seek(offset)
        f.write(data)  # Sobrescribe ÚNICAMENTE ese registro
        # El resto del archivo permanece intacto en disco
```

---

## 3. Arquitectura del Índice Primario JSON

El archivo `indice.json` actúa como un mapa asociativo en memoria secundaria:
$$\text{Índice}: \text{ID de Contacto} \longrightarrow \text{Número de Registro Físico (0, 1, 2, \dots)}$$

### Estructura de `indice.json`
```json
{
  "101": 0,
  "102": 1,
  "103": 2,
  "104": 3,
  "105": 4
}
```

### ¿Por qué la búsqueda con índice es más eficiente que la secuencial?
- **Búsqueda Secuencial ($O(N)$):** Requiere leer registro por registro desde el inicio hasta encontrar la clave. Con $N = 100,000$ contactos, requiere en promedio $50,000$ operaciones de I/O de disco.
- **Búsqueda con Índice ($O(1)$ amortizado):** 
  1. Se consulta la tabla hash del índice por ID en memoria RAM en tiempo $O(1)$.
  2. Se obtiene inmediatamente el `record_num`.
  3. Se realiza una **única operación de I/O** invocando `seek(record_num * 256)`.
- **Rendimiento:** La latencia de búsqueda pasa de segundos a menos de $1$ milisegundo.

---

## 4. Verificación de Integridad Criptográfica (SHA-256)

Para proteger la integridad de los datos frente a modificaciones externas accidentales o maliciosas:
1. Cada vez que se agrega, modifica o elimina lógicamente un contacto, se calcula el hash SHA-256 de `contactos.dat` y se almacena en `contactos.sha256`.
2. Al iniciar la aplicación, se recalcula el hash del archivo y se compara con el almacenado.
3. Si difieren, el sistema lanza una **alerta visual preventiva**, advirtiendo que el archivo fue manipulado fuera del software.

### Detección de Alteración Manual
Al modificar intencionalmente un solo byte en `contactos.dat` con un editor hexadecimal o mediante la herramienta de simulación incorporada:
- **Hash almacenado:** `10564b27c85d3503a74ef6ba7cb7d...`
- **Hash calculado post-alteración:** `8c3b7a812dfb49021a5ef...`
- **Diagnóstico:** Discrepancia detectada. La aplicación protege la información y no sobrescribe el archivo hasta que el usuario decida restaurar un respaldo o reconstruir el índice.

---

## 5. Respaldos Comprimidos ZIP y Análisis de Reducción

La aplicación incorpora un gestor de respaldos que comprime con el algoritmo DEFLATE (`zipfile`):
- `contactos.dat`
- `indice.json`
- `contactos.sha256`

### Comparativa de Espacio
| Métrica | Valor |
| :--- | :--- |
| **Tamaño Original sin comprimir** | **3,297 bytes** (3.22 KB) |
| **Tamaño Comprimido en ZIP** | **1,252 bytes** (1.22 KB) |
| **Espacio Ahorrado** | **2,045 bytes** |
| **Porcentaje de Reducción** | **62.0 %** de compresión |

El elevado ratio de compresión se debe al relleno uniforme de espacios (`0x20`) propio de los registros de tamaño fijo, que resulta ideal para el algoritmo de longitud variable de compresión DEFLATE.

---

## 6. Funcionalidades Profesionales Implementadas

1. **Fondo Animado Liquid Glass:** Renderizado dinámico mediante Canvas y PIL/Pillow con blobs gaussianos en movimiento sinusoidal.
2. **Eliminación Lógica y Restauración:** Campo `estado` (`'A'`/`'D'`) para conservar auditoría y permitir recuperar contactos borrados por error.
3. **Reconstrucción Automática de Índice:** Si `indice.json` se daña o borra, se regenera automáticamente escaneando los 256 bytes de cada registro.
4. **Exportaciones Triples:** JSON estructurado, Reporte PDF formal con `fpdf2` y tabla apaisada, y CSV con BOM UTF-8 para Microsoft Excel.
5. **Panel de Información del Sistema:** Inspección de permisos con `os.access()` (lectura/escritura) y tamaño con `os.stat()`.

