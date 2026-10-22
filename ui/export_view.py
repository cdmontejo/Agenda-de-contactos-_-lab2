# -*- coding: utf-8 -*-
"""
Vista de Exportación de Datos.

Permite exportar todos los contactos a:
  - Formato JSON estructurado (requisito)
  - Reporte PDF profesional con tabla y fecha de generación (requisito)
  - Formato CSV compatible con Excel
"""

import tkinter as tk
import os
import glob
from datetime import datetime
import logging

from ui.theme import (
    BG_BASE, BG_CARD, TEXT_PRIMARY, TEXT_SECONDARY, TEXT_MUTED,
    ACCENT_PRIMARY, COLOR_SUCCESS, COLOR_INFO, FONT_HEADING_LG,
    FONT_HEADING_SM, FONT_BODY, FONT_BODY_BOLD, FONT_SMALL
)
from ui.components import GlassCard, GlassButton, GlassTable, Toast
from ui.dialogs import InfoDialog
from config import EXPORTS_DIR

logger = logging.getLogger(__name__)


class ExportView(tk.Frame):
    """
    Panel de control para exportación de registros y reportes.
    """

    def __init__(self, parent, export_manager, **kwargs):
        super().__init__(parent, bg=BG_BASE, **kwargs)
        self.exporter = export_manager

        self._build_ui()
        self.refresh_history()

    def _build_ui(self):
        # Encabezado
        head = tk.Frame(self, bg=BG_BASE)
        head.pack(fill='x', padx=24, pady=(20, 16))

        h1 = tk.Label(head, text="Exportación & Reportes", font=FONT_HEADING_LG,
                      fg=TEXT_PRIMARY, bg=BG_BASE, anchor='w')
        h1.pack(fill='x')

        sub = tk.Label(head, text="Generación de respaldos en JSON y reportes impresos en PDF con fecha",
                       font=FONT_SMALL, fg=TEXT_SECONDARY, bg=BG_BASE, anchor='w')
        sub.pack(fill='x', pady=(4, 0))

        # Tarjetas de formatos (3 en fila)
        cards_row = tk.Frame(self, bg=BG_BASE)
        cards_row.pack(fill='x', padx=24, pady=(0, 20))

        # Tarjeta JSON
        c_json = GlassCard(cards_row, title="Exportar a JSON", subtitle="Estructura completa de datos")
        c_json.pack(side='left', fill='both', expand=True, padx=(0, 8))

        lbl_j = tk.Label(
            c_json.content, text="Genera un archivo JSON con todos los contactos activos e integridad preservada.",
            font=FONT_SMALL, fg=TEXT_SECONDARY, bg=BG_CARD, wraplength=260, justify='left'
        )
        lbl_j.pack(fill='x', pady=(0, 16))

        btn_json = GlassButton(c_json.content, text="Generar JSON", icon="📄", variant='primary',
                               width=150, command=self.on_export_json)
        btn_json.pack(anchor='w')

        # Tarjeta PDF
        c_pdf = GlassCard(cards_row, title="Reporte en PDF", subtitle="Documento formal con fecha")
        c_pdf.pack(side='left', fill='both', expand=True, padx=4)

        lbl_p = tk.Label(
            c_pdf.content, text="Genera un reporte PDF con fpdf2 en tabla formateada y fecha exacta de emisión.",
            font=FONT_SMALL, fg=TEXT_SECONDARY, bg=BG_CARD, wraplength=260, justify='left'
        )
        lbl_p.pack(fill='x', pady=(0, 16))

        btn_pdf = GlassButton(c_pdf.content, text="Generar PDF", icon="📊", variant='info',
                              width=150, command=self.on_export_pdf)
        btn_pdf.pack(anchor='w')

        # Tarjeta CSV
        c_csv = GlassCard(cards_row, title="Exportar a CSV", subtitle="Compatible con Excel / Calc")
        c_csv.pack(side='left', fill='both', expand=True, padx=(8, 0))

        lbl_c = tk.Label(
            c_csv.content, text="Archivo delimitado por comas con codificación UTF-8 BOM para apertura directa.",
            font=FONT_SMALL, fg=TEXT_SECONDARY, bg=BG_CARD, wraplength=260, justify='left'
        )
        lbl_c.pack(fill='x', pady=(0, 16))

        btn_csv = GlassButton(c_csv.content, text="Generar CSV", icon="📋", variant='secondary',
                              width=150, command=self.on_export_csv)
        btn_csv.pack(anchor='w')

        # Historial de Exportaciones
        hist_card = GlassCard(self, title="Historial de Archivos Exportados", subtitle="Archivos disponibles en la carpeta exports/")
        hist_card.pack(fill='both', expand=True, padx=24, pady=(0, 20))

        cols = ['filename', 'tipo', 'tamano', 'fecha']
        heads = ['Nombre de Archivo', 'Tipo', 'Tamaño', 'Fecha de Creación']
        widths = [260, 90, 100, 160]

        self.table_history = GlassTable(hist_card.content, columns=cols, headings=heads, widths=widths)
        self.table_history.pack(fill='both', expand=True, pady=(0, 10))

        btn_open_folder = GlassButton(hist_card.content, text="Abrir Carpeta de Exportaciones", icon="📁",
                                      variant='secondary', width=240, command=self.on_open_folder)
        btn_open_folder.pack(anchor='w')

    def refresh_history(self):
        """Escanea la carpeta de exportaciones y llena la tabla."""
        files = glob.glob(os.path.join(EXPORTS_DIR, "*.*"))
        items = []
        for f in files:
            name = os.path.basename(f)
            if name.endswith('.gitkeep'):
                continue
            ext = name.split('.')[-1].upper()
            stat = os.stat(f)
            size_str = f"{stat.st_size:,} bytes"
            mod_time = datetime.fromtimestamp(stat.st_mtime).strftime('%Y-%m-%d %H:%M:%S')
            items.append({
                'id': name,
                'filename': name,
                'tipo': ext,
                'tamano': size_str,
                'fecha': mod_time
            })
        items.sort(key=lambda x: x['fecha'], reverse=True)
        self.table_history.load_data(items)

    def on_export_json(self):
        ok, msg, path = self.exporter.export_json()
        if ok:
            Toast(self, "Exportación JSON generada con éxito", toast_type='success')
            InfoDialog(self, "Exportación JSON", f"Archivo generado:\n{path}")
            self.refresh_history()
        else:
            Toast(self, msg, toast_type='error')

    def on_export_pdf(self):
        ok, msg, path = self.exporter.export_pdf()
        if ok:
            Toast(self, "Reporte PDF generado exitosamente", toast_type='success')
            InfoDialog(self, "Reporte PDF", f"Reporte generado con fpdf2:\n{path}")
            self.refresh_history()
        else:
            Toast(self, msg, toast_type='error')

    def on_export_csv(self):
        ok, msg, path = self.exporter.export_csv()
        if ok:
            Toast(self, "Archivo CSV generado exitosamente", toast_type='success')
            InfoDialog(self, "Exportación CSV", f"Archivo generado:\n{path}")
            self.refresh_history()
        else:
            Toast(self, msg, toast_type='error')

    def on_open_folder(self):
        try:
            os.startfile(EXPORTS_DIR)
        except Exception as e:
            Toast(self, f"No se pudo abrir la carpeta: {e}", toast_type='error')

