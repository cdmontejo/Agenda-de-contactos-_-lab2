# -*- coding: utf-8 -*-
"""
Vista de Ayuda y Documentación del Sistema (Requisito: Ayuda simulada).

Explica la arquitectura técnica, atajos de teclado y funcionamiento
del acceso aleatorio con seek() y tell().
"""

import tkinter as tk
import logging

from ui.theme import (
    BG_BASE, BG_CARD, TEXT_PRIMARY, TEXT_SECONDARY, ACCENT_PRIMARY,
    FONT_HEADING_LG, FONT_HEADING_SM, FONT_BODY, FONT_SMALL, FONT_MONO
)
from ui.components import GlassCard

logger = logging.getLogger(__name__)


class HelpView(tk.Frame):
    """
    Panel de ayuda, documentación de arquitectura y atajos.
    """

    def __init__(self, parent, **kwargs):
        super().__init__(parent, bg=BG_BASE, **kwargs)
        self._build_ui()

    def _build_ui(self):
        head = tk.Frame(self, bg=BG_BASE)
        head.pack(fill='x', padx=24, pady=(20, 16))

        h1 = tk.Label(head, text="Centro de Ayuda & Especificaciones", font=FONT_HEADING_LG,
                      fg=TEXT_PRIMARY, bg=BG_BASE, anchor='w')
        h1.pack(fill='x')

        sub = tk.Label(head, text="Documentación técnica sobre acceso aleatorio, estructura de registros y atajos de teclado",
                       font=FONT_SMALL, fg=TEXT_SECONDARY, bg=BG_BASE, anchor='w')
        sub.pack(fill='x', pady=(4, 0))

        content_box = tk.Frame(self, bg=BG_BASE)
        content_box.pack(fill='both', expand=True, padx=24, pady=(0, 20))

        # Tarjeta 1: Estructura del Registro Fijo (256 bytes)
        c_spec = GlassCard(content_box, title="Estructura del Registro Fijo (256 Bytes)", subtitle="Organización binaria por contacto")
        c_spec.pack(fill='x', pady=(0, 16))

        spec_text = (
            "Cada contacto se almacena de forma contigua en 'contactos.dat' ocupando exactamente 256 bytes:\n\n"
            "  • ID:        10 bytes  (numérico entero, alineado con ceros/espacios)\n"
            "  • Nombre:    80 bytes  (texto UTF-8 con soporte para tildes y caracteres especiales)\n"
            "  • Teléfono:  20 bytes  (cadena telefónica)\n"
            "  • Correo:    80 bytes  (dirección electrónica)\n"
            "  • Ciudad:    50 bytes  (ciudad de residencia)\n"
            "  • Estado:     1 byte   ('A'=Activo, 'D'=Eliminado lógicamente)\n"
            "  • Padding:   14 bytes  (relleno con espacios para alineación a 256 bytes)\n"
            "  • Newline:    1 byte   (salto de línea '\\n' para depuración e inspección)\n"
            "  -----------------------------------------------------------------------\n"
            "  TOTAL:      256 bytes por registro físico."
        )
        lbl_spec = tk.Label(c_spec.content, text=spec_text, font=FONT_MONO, fg=TEXT_PRIMARY,
                            bg=BG_CARD, justify='left', anchor='w')
        lbl_spec.pack(fill='x')

        # Tarjeta 2: Acceso Aleatorio e Índice Primario
        c_seek = GlassCard(content_box, title="Acceso Aleatorio con seek() y tell()", subtitle="Eficiencia computacional O(1)")
        c_seek.pack(fill='x', pady=(0, 16))

        seek_text = (
            "¿Cómo funciona la búsqueda y modificación sin leer todo el archivo?\n\n"
            "1. Consulta del Índice Primario ('indice.json'):\n"
            "   Dada una clave 'ID', el índice en memoria retorna directamente el 'número de registro' (0, 1, 2, ...).\n\n"
            "2. Posicionamiento Directo con seek():\n"
            "   archivo.seek(numero_registro * 256) traslada la aguja del disco en tiempo constante O(1).\n\n"
            "3. Demostración con tell():\n"
            "   archivo.tell() reporta la posición exacta en bytes antes y después de cada lectura o escritura.\n\n"
            "4. Modificación in-place:\n"
            "   Al editar un contacto o marcarlo como eliminado ('D'), solo se sobrescriben 256 bytes en su offset "
            "sin alterar ni reescribir ningún otro registro del archivo."
        )
        lbl_seek = tk.Label(c_seek.content, text=seek_text, font=FONT_BODY, fg=TEXT_SECONDARY,
                            bg=BG_CARD, justify='left', anchor='w')
        lbl_seek.pack(fill='x')

        # Tarjeta 3: Atajos de Teclado
        c_keys = GlassCard(content_box, title="Atajos de Teclado", subtitle="Productividad rápida")
        c_keys.pack(fill='x')

        keys_text = (
            "• Ctrl + N : Registrar nuevo contacto\n"
            "• Ctrl + F : Búsqueda rápida por ID con seek()\n"
            "• Ctrl + E : Exportar a formato JSON\n"
            "• Ctrl + B : Crear respaldo ZIP comprimido\n"
            "• F5       : Refrescar registros y estadísticas"
        )
        lbl_keys = tk.Label(c_keys.content, text=keys_text, font=FONT_BODY, fg=TEXT_PRIMARY,
                            bg=BG_CARD, justify='left', anchor='w')
        lbl_keys.pack(fill='x')
