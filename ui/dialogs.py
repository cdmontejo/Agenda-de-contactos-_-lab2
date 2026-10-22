# -*- coding: utf-8 -*-
"""
Diálogos modales con diseño Liquid Glass.

Incluye:
  - ConfirmDialog: Diálogo de confirmación para acciones críticas
  - InfoDialog: Diálogo informativo
  - ErrorDialog: Diálogo de error
  - FileInfoDialog: Información técnica del archivo (stat, access, permisos)
  - BackupResultDialog: Comparación de tamaño original vs comprimido ZIP
  - ContactDetailDialog: Vista detallada de un contacto
"""

import tkinter as tk
import os
import logging

from ui.theme import (
    BG_BASE, BG_CARD, BG_GLASS, BORDER_GLASS, TEXT_PRIMARY,
    TEXT_SECONDARY, TEXT_MUTED, ACCENT_PRIMARY, COLOR_SUCCESS,
    COLOR_WARNING, COLOR_ERROR, COLOR_INFO, FONT_FAMILY,
    FONT_HEADING_SM, FONT_BODY, FONT_BODY_BOLD, FONT_SMALL,
    FONT_SMALL_BOLD, FONT_MONO
)
from ui.components import GlassButton

logger = logging.getLogger(__name__)


class BaseModalDialog(tk.Toplevel):
    """Clase base para todos los diálogos modales con efecto cristal."""

    def __init__(self, parent, title: str = "", width: int = 420, height: int = 240):
        super().__init__(parent)
        self.title(title)
        self.geometry(f"{width}x{height}")
        self.configure(bg=BG_BASE)
        self.resizable(False, False)
        self.transient(parent)
        self.grab_set()

        # Centrar en la ventana padre
        self.update_idletasks()
        try:
            px = parent.winfo_rootx()
            py = parent.winfo_rooty()
            pw = parent.winfo_width()
            ph = parent.winfo_height()
            x = px + (pw - width) // 2
            y = py + (ph - height) // 2
            self.geometry(f"+{x}+{y}")
        except Exception:
            pass

        # Contenedor de cristal exterior
        self.outer_border = tk.Frame(self, bg=BORDER_GLASS, padx=1, pady=1)
        self.outer_border.pack(fill='both', expand=True, padx=12, pady=12)

        self.main_frame = tk.Frame(self.outer_border, bg=BG_CARD, padx=20, pady=18)
        self.main_frame.pack(fill='both', expand=True)

        if title:
            t_lbl = tk.Label(
                self.main_frame, text=title, font=FONT_HEADING_SM,
                fg=TEXT_PRIMARY, bg=BG_CARD, anchor='w'
            )
            t_lbl.pack(fill='x', pady=(0, 12))


class ConfirmDialog(BaseModalDialog):
    """Diálogo de confirmación interactivo."""

    def __init__(self, parent, title: str, message: str,
                 confirm_text: str = "Confirmar", cancel_text: str = "Cancelar",
                 variant: str = 'danger'):
        super().__init__(parent, title=title, width=420, height=200)
        self.result = False

        msg_lbl = tk.Label(
            self.main_frame, text=message, font=FONT_BODY,
            fg=TEXT_PRIMARY, bg=BG_CARD, wraplength=360, justify='left'
        )
        msg_lbl.pack(fill='both', expand=True, pady=(0, 16))

        btn_box = tk.Frame(self.main_frame, bg=BG_CARD)
        btn_box.pack(fill='x')

        cancel_btn = GlassButton(
            btn_box, text=cancel_text, variant='secondary',
            width=120, command=self._on_cancel
        )
        cancel_btn.pack(side='right', padx=(8, 0))

        confirm_btn = GlassButton(
            btn_box, text=confirm_text, variant=variant,
            width=130, command=self._on_confirm
        )
        confirm_btn.pack(side='right')

        self.wait_window()

    def _on_confirm(self):
        self.result = True
        self.destroy()

    def _on_cancel(self):
        self.result = False
        self.destroy()


class InfoDialog(BaseModalDialog):
    """Diálogo informativo con botón de aceptar."""

    def __init__(self, parent, title: str, message: str):
        super().__init__(parent, title=title, width=420, height=200)

        msg_lbl = tk.Label(
            self.main_frame, text=message, font=FONT_BODY,
            fg=TEXT_PRIMARY, bg=BG_CARD, wraplength=360, justify='left'
        )
        msg_lbl.pack(fill='both', expand=True, pady=(0, 16))

        btn_box = tk.Frame(self.main_frame, bg=BG_CARD)
        btn_box.pack(fill='x')

        ok_btn = GlassButton(
            btn_box, text="Aceptar", variant='primary',
            width=120, command=self.destroy
        )
        ok_btn.pack(side='right')


class ErrorDialog(BaseModalDialog):
    """Diálogo de error."""

    def __init__(self, parent, title: str, message: str):
        super().__init__(parent, title=f"⚠ {title}", width=440, height=220)

        msg_lbl = tk.Label(
            self.main_frame, text=message, font=FONT_BODY,
            fg=COLOR_ERROR, bg=BG_CARD, wraplength=380, justify='left'
        )
        msg_lbl.pack(fill='both', expand=True, pady=(0, 16))

        btn_box = tk.Frame(self.main_frame, bg=BG_CARD)
        btn_box.pack(fill='x')

        ok_btn = GlassButton(
            btn_box, text="Entendido", variant='secondary',
            width=120, command=self.destroy
        )
        ok_btn.pack(side='right')


class FileInfoDialog(BaseModalDialog):
    """
    Diálogo para mostrar metadatos técnicos del archivo según
    requisito del laboratorio (os.stat, os.access, tamaño, fecha).
    """

    def __init__(self, parent, file_info: dict):
        super().__init__(parent, title="📄 Información Técnica del Archivo", width=520, height=360)

        grid_frame = tk.Frame(self.main_frame, bg=BG_CARD)
        grid_frame.pack(fill='both', expand=True, pady=(0, 12))

        # Formatear datos
        size_bytes = file_info.get('size', 0)
        size_kb = size_bytes / 1024.0
        total_records = file_info.get('total_records', 0)
        modified = file_info.get('modified', 'N/A')
        readable = "✓ Permitido" if file_info.get('readable') else "✕ Denegado"
        writable = "✓ Permitido" if file_info.get('writable') else "✕ Denegado"
        path = file_info.get('path', 'contactos.dat')

        rows = [
            ("Ruta de archivo:", path),
            ("Tamaño físico:", f"{size_bytes:,} bytes ({size_kb:.2f} KB)"),
            ("Tamaño por registro:", "256 bytes (fijo, UTF-8)"),
            ("Total de registros:", f"{total_records} registros"),
            ("Última modificación:", modified),
            ("Permiso de lectura (os.access):", readable),
            ("Permiso de escritura (os.access):", writable),
            ("Codificación:", "UTF-8 con relleno de bytes (0x20)"),
        ]

        for i, (label, val) in enumerate(rows):
            lbl = tk.Label(grid_frame, text=label, font=FONT_SMALL_BOLD,
                           fg=TEXT_SECONDARY, bg=BG_CARD, anchor='w')
            lbl.grid(row=i, column=0, sticky='w', pady=3)

            val_lbl = tk.Label(grid_frame, text=val, font=FONT_MONO if 'bytes' in val or 'access' in label else FONT_SMALL,
                               fg=TEXT_PRIMARY, bg=BG_CARD, anchor='w')
            val_lbl.grid(row=i, column=1, sticky='w', padx=(12, 0), pady=3)

        btn_box = tk.Frame(self.main_frame, bg=BG_CARD)
        btn_box.pack(fill='x')

        close_btn = GlassButton(btn_box, text="Cerrar", variant='primary', width=120, command=self.destroy)
        close_btn.pack(side='right')


class BackupResultDialog(BaseModalDialog):
    """
    Diálogo para mostrar el resultado del respaldo ZIP con
    comparación de tamaño original vs comprimido (requisito del laboratorio).
    """

    def __init__(self, parent, info: dict):
        super().__init__(parent, title="📦 Respaldo Comprimido Exitoso", width=480, height=320)

        orig = info.get('original_size', 0)
        comp = info.get('compressed_size', 0)
        path = info.get('filepath', '')
        ratio = ((orig - comp) / orig * 100) if orig > 0 else 0

        info_frame = tk.Frame(self.main_frame, bg=BG_CARD)
        info_frame.pack(fill='both', expand=True, pady=(0, 12))

        lines = [
            ("Archivo generado:", os.path.basename(path)),
            ("Tamaño original:", f"{orig:,} bytes ({orig / 1024:.2f} KB)"),
            ("Tamaño comprimido ZIP:", f"{comp:,} bytes ({comp / 1024:.2f} KB)"),
            ("Ahorro de espacio:", f"{ratio:.1f}% de reducción"),
            ("Algoritmo de compresión:", "DEFLATE (zipfile estándar)"),
            ("Archivos incluidos:", "contactos.dat, indice.json, contactos.sha256")
        ]

        for i, (label, val) in enumerate(lines):
            l = tk.Label(info_frame, text=label, font=FONT_SMALL_BOLD, fg=TEXT_SECONDARY, bg=BG_CARD, anchor='w')
            l.grid(row=i, column=0, sticky='w', pady=4)

            v = tk.Label(info_frame, text=val, font=FONT_MONO if 'bytes' in val else FONT_SMALL,
                         fg=COLOR_SUCCESS if 'reducción' in val else TEXT_PRIMARY, bg=BG_CARD, anchor='w')
            v.grid(row=i, column=1, sticky='w', padx=(12, 0), pady=4)

        btn_box = tk.Frame(self.main_frame, bg=BG_CARD)
        btn_box.pack(fill='x')

        ok_btn = GlassButton(btn_box, text="Aceptar", variant='primary', width=120, command=self.destroy)
        ok_btn.pack(side='right')

