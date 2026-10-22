# -*- coding: utf-8 -*-
"""
Vista de Herramientas de Mantenimiento y Seguridad.

Permite:
  - Verificar integridad criptográfica SHA-256 (requisito)
  - Crear respaldo comprimido ZIP con comparación de tamaño (requisito)
  - Consultar información técnica del archivo (stat, access) (requisito)
  - Reconstruir índice primario desde registros
  - Restaurar respaldo ZIP
  - Simular alteración externa para pruebas de integridad
"""

import tkinter as tk
import os
import logging

from ui.theme import (
    BG_BASE, BG_CARD, TEXT_PRIMARY, TEXT_SECONDARY, COLOR_SUCCESS,
    COLOR_WARNING, COLOR_ERROR, COLOR_INFO, FONT_HEADING_LG,
    FONT_HEADING_SM, FONT_BODY, FONT_SMALL
)
from ui.components import GlassCard, GlassButton, GlassTable, Toast
from ui.dialogs import (
    FileInfoDialog, BackupResultDialog, ConfirmDialog, InfoDialog, ErrorDialog
)
from config import CONTACTS_FILE

logger = logging.getLogger(__name__)


class ToolsView(tk.Frame):
    """
    Centro de herramientas técnicas y diagnósticos de almacenamiento.
    """

    def __init__(self, parent, contact_service, backup_manager, **kwargs):
        super().__init__(parent, bg=BG_BASE, **kwargs)
        self.service = contact_service
        self.backuper = backup_manager

        self._build_ui()
        self.refresh_backups()

    def _build_ui(self):
        # Encabezado
        head = tk.Frame(self, bg=BG_BASE)
        head.pack(fill='x', padx=24, pady=(20, 16))

        h1 = tk.Label(head, text="Centro de Herramientas & Seguridad", font=FONT_HEADING_LG,
                      fg=TEXT_PRIMARY, bg=BG_BASE, anchor='w')
        h1.pack(fill='x')

        sub = tk.Label(head, text="Operaciones de diagnóstico de integridad SHA-256, respaldos ZIP e información del sistema",
                       font=FONT_SMALL, fg=TEXT_SECONDARY, bg=BG_BASE, anchor='w')
        sub.pack(fill='x', pady=(4, 0))

        # Tarjetas de Herramientas Principales (Grid 2x2)
        grid_frame = tk.Frame(self, bg=BG_BASE)
        grid_frame.pack(fill='x', padx=24, pady=(0, 20))

        # 1. Integridad SHA-256
        c_hash = GlassCard(grid_frame, title="Verificar Integridad", subtitle="Cálculo de hash SHA-256")
        c_hash.grid(row=0, column=0, sticky='nsew', padx=(0, 8), pady=(0, 10))

        lbl_h = tk.Label(
            c_hash.content, text="Recalcula el hash SHA-256 del archivo contactos.dat y lo compara con el valor almacenado para detectar manipulaciones externas.",
            font=FONT_SMALL, fg=TEXT_SECONDARY, bg=BG_CARD, wraplength=340, justify='left'
        )
        lbl_h.pack(fill='x', pady=(0, 12))

        b_row_h = tk.Frame(c_hash.content, bg=BG_CARD)
        b_row_h.pack(fill='x')

        btn_verify = GlassButton(b_row_h, text="Verificar Ahora", icon="🛡", variant='primary',
                                 width=140, command=self.on_verify_integrity)
        btn_verify.pack(side='left', padx=(0, 8))

        btn_corrupt = GlassButton(b_row_h, text="Simular Alteración", icon="⚡", variant='danger',
                                  width=150, command=self.on_simulate_tamper)
        btn_corrupt.pack(side='left')

        # 2. Respaldo Comprimido ZIP
        c_zip = GlassCard(grid_frame, title="Respaldo Comprimido", subtitle="Empaquetado zipfile (DEFLATE)")
        c_zip.grid(row=0, column=1, sticky='nsew', padx=(8, 0), pady=(0, 10))

        lbl_z = tk.Label(
            c_zip.content, text="Genera un respaldo ZIP con contactos.dat, indice.json y contactos.sha256, mostrando el tamaño original vs comprimido.",
            font=FONT_SMALL, fg=TEXT_SECONDARY, bg=BG_CARD, wraplength=340, justify='left'
        )
        lbl_z.pack(fill='x', pady=(0, 12))

        btn_backup = GlassButton(c_zip.content, text="Crear Respaldo ZIP", icon="📦", variant='success',
                                 width=170, command=self.on_create_backup)
        btn_backup.pack(anchor='w')

        # 3. Información Técnica del Archivo
        c_info = GlassCard(grid_frame, title="Información del Archivo", subtitle="Metadatos vía os.stat y os.access")
        c_info.grid(row=1, column=0, sticky='nsew', padx=(0, 8))

        lbl_i = tk.Label(
            c_info.content, text="Muestra tamaño físico en bytes, fecha de última modificación y permisos de lectura/escritura del archivo.",
            font=FONT_SMALL, fg=TEXT_SECONDARY, bg=BG_CARD, wraplength=340, justify='left'
        )
        lbl_i.pack(fill='x', pady=(0, 12))

        btn_info = GlassButton(c_info.content, text="Ver Información", icon="ℹ", variant='secondary',
                               width=150, command=self.on_show_file_info)
        btn_info.pack(anchor='w')

        # 4. Mantenimiento del Índice Primario
        c_idx = GlassCard(grid_frame, title="Reconstruir Índice", subtitle="Recuperación ante corrupción")
        c_idx.grid(row=1, column=1, sticky='nsew', padx=(8, 0))

        lbl_ix = tk.Label(
            c_idx.content, text="Si el archivo indice.json se corrompe o elimina, esta función lee secuencialmente el archivo de registros y regenera el mapeo ID -> registro.",
            font=FONT_SMALL, fg=TEXT_SECONDARY, bg=BG_CARD, wraplength=340, justify='left'
        )
        lbl_ix.pack(fill='x', pady=(0, 12))

        btn_rebuild = GlassButton(c_idx.content, text="Reconstruir Índice", icon="⚙", variant='secondary',
                                  width=160, command=self.on_rebuild_index)
        btn_rebuild.pack(anchor='w')

        grid_frame.columnconfigure(0, weight=1)
        grid_frame.columnconfigure(1, weight=1)

        # Sección de Respaldos Disponibles y Restauración
        b_card = GlassCard(self, title="Respaldos ZIP Disponibles", subtitle="Seleccione un respaldo para restaurar")
        b_card.pack(fill='both', expand=True, padx=24, pady=(0, 20))

        cols = ['filename', 'tamano', 'fecha']
        heads = ['Archivo ZIP', 'Tamaño Comprimido', 'Fecha']
        widths = [260, 120, 160]

        self.table_backups = GlassTable(b_card.content, columns=cols, headings=heads, widths=widths)
        self.table_backups.pack(fill='both', expand=True, pady=(0, 10))

        btn_row_b = tk.Frame(b_card.content, bg=BG_CARD)
        btn_row_b.pack(fill='x')

        btn_restore = GlassButton(btn_row_b, text="Restaurar Seleccionado", icon="↺", variant='danger',
                                  width=180, command=self.on_restore_backup)
        btn_restore.pack(side='left', padx=(0, 8))

        btn_refresh_b = GlassButton(btn_row_b, text="Refrescar Lista", icon="↻", variant='secondary',
                                    width=130, command=self.refresh_backups)
        btn_refresh_b.pack(side='left')

    def refresh_backups(self):
        """Lista los respaldos disponibles."""
        backups = self.backuper.list_backups()
        items = []
        for b in backups:
            items.append({
                'id': b.get('filename', ''),
                'filename': b.get('filename', ''),
                'tamano': f"{b.get('size', 0):,} bytes",
                'fecha': b.get('created', '')
            })
        self.table_backups.load_data(items)

    def on_verify_integrity(self):
        ok, msg = self.service.verify_integrity()
        if ok:
            Toast(self, "Verificación exitosa: Los datos están íntegros", toast_type='success')
            InfoDialog(self, "Integridad de Datos", f"✓ {msg}\n\nEl archivo no ha sido alterado externamente.")
        else:
            Toast(self, "ALERTA DE INTEGRIDAD: Hash no coincide", toast_type='error')
            ErrorDialog(self, "Falla de Integridad", f"⚠ {msg}\n\nEl archivo contactos.dat ha sido modificado por un programa externo o está corrupto.")

    def on_simulate_tamper(self):
        """
        Altera manualmente un byte del archivo para evidenciar la detección
        de modificación externa (requisito del informe del laboratorio).
        """
        dlg = ConfirmDialog(
            self, title="Simulación de Alteración Externa",
            message="¿Desea alterar un byte del archivo contactos.dat para probar que el sistema detecta modificaciones no autorizadas?\n\n(Requisito del laboratorio para evidencia en capturas).",
            confirm_text="Alterar Archivo", variant='danger'
        )
        if not dlg.result:
            return

        try:
            if not os.path.exists(CONTACTS_FILE) or os.path.getsize(CONTACTS_FILE) == 0:
                Toast(self, "Primero registre al menos un contacto", toast_type='warning')
                return

            # Escribir un byte corrupto directamente al archivo
            with open(CONTACTS_FILE, 'r+b') as f:
                f.seek(15)  # Alterar posición 15
                f.write(b'X')

            Toast(self, "Archivo alterado externamente con éxito", toast_type='warning')
            InfoDialog(
                self, "Archivo Alterado",
                "Se ha modificado el byte #15 de 'contactos.dat' externamente.\n\n"
                "Ahora presione 'Verificar Ahora' o reinicie la aplicación para "
                "observar la detección automática de discrepancia SHA-256."
            )
        except Exception as e:
            Toast(self, f"Error al alterar archivo: {e}", toast_type='error')

    def on_create_backup(self):
        ok, msg, info = self.backuper.create_backup()
        if ok:
            Toast(self, "Respaldo ZIP creado exitosamente", toast_type='success')
            BackupResultDialog(self, info)
            self.refresh_backups()
        else:
            Toast(self, msg, toast_type='error')

    def on_show_file_info(self):
        info = self.service.get_file_info()
        FileInfoDialog(self, info)

    def on_rebuild_index(self):
        dlg = ConfirmDialog(
            self, title="Confirmar Reconstrucción",
            message="¿Desea escanear el archivo contactos.dat y reconstruir el archivo indice.json por completo?",
            confirm_text="Reconstruir", variant='primary'
        )
        if dlg.result:
            ok, msg = self.service.rebuild_index()
            if ok:
                Toast(self, msg, toast_type='success')
                InfoDialog(self, "Índice Reconstruido", msg)
            else:
                Toast(self, msg, toast_type='error')

    def on_restore_backup(self):
        sel = self.table_backups.get_selected()
        if not sel:
            Toast(self, "Seleccione un respaldo de la tabla para restaurar", toast_type='warning')
            return

        filename = sel.get('filename')
        dlg = ConfirmDialog(
            self, title="Restaurar Respaldo",
            message=f"¿Desea restaurar el estado desde '{filename}'?\n\nSe creará una copia de seguridad automática antes de aplicar los datos restaurados.",
            confirm_text="Restaurar", variant='danger'
        )
        if dlg.result:
            filepath = os.path.join(self.backuper.backups_dir, filename)
            ok, msg = self.backuper.restore_backup(filepath)
            if ok:
                Toast(self, "Datos restaurados exitosamente", toast_type='success')
                InfoDialog(self, "Restauración Completa", msg)
            else:
                Toast(self, msg, toast_type='error')

