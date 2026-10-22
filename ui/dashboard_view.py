# -*- coding: utf-8 -*-
"""
Vista de Dashboard principal con diseño Liquid Glass.

Muestra métricas clave, estado de integridad de datos SHA-256,
acciones rápidas y contactos recientes.
"""

import tkinter as tk
import logging

from ui.theme import (
    BG_BASE, BG_CARD, BORDER_GLASS, TEXT_PRIMARY, TEXT_SECONDARY,
    ACCENT_PRIMARY, COLOR_SUCCESS, COLOR_ERROR, COLOR_INFO,
    FONT_HEADING_LG, FONT_HEADING_SM, FONT_BODY, FONT_SMALL
)
from ui.components import GlassCard, StatCard, GlassButton, GlassTable

logger = logging.getLogger(__name__)


class DashboardView(tk.Frame):
    """
    Panel de control ejecutivo de la aplicación.
    """

    def __init__(self, parent, contact_service, on_navigate=None, **kwargs):
        super().__init__(parent, bg=BG_BASE, **kwargs)
        self.service = contact_service
        self.on_navigate = on_navigate

        self._build_ui()
        self.refresh()

    def _build_ui(self):
        # Encabezado
        head_frame = tk.Frame(self, bg=BG_BASE)
        head_frame.pack(fill='x', padx=24, pady=(20, 16))

        h1 = tk.Label(
            head_frame, text="Panel Ejecutivo", font=FONT_HEADING_LG,
            fg=TEXT_PRIMARY, bg=BG_BASE, anchor='w'
        )
        h1.pack(fill='x')

        sub = tk.Label(
            head_frame, text="Resumen del sistema de archivos de acceso aleatorio e indexación primaria",
            font=FONT_SMALL, fg=TEXT_SECONDARY, bg=BG_BASE, anchor='w'
        )
        sub.pack(fill='x', pady=(4, 0))

        # Tarjetas de estadísticas (Fila de 4)
        stats_frame = tk.Frame(self, bg=BG_BASE)
        stats_frame.pack(fill='x', padx=24, pady=(0, 20))

        self.card_total = StatCard(stats_frame, "Total Registros", "0", icon="📇", accent_color=ACCENT_PRIMARY)
        self.card_total.pack(side='left', fill='both', expand=True, padx=(0, 10))

        self.card_active = StatCard(stats_frame, "Activos", "0", icon="✓", accent_color=COLOR_SUCCESS)
        self.card_active.pack(side='left', fill='both', expand=True, padx=5)

        self.card_deleted = StatCard(stats_frame, "Eliminados", "0", icon="🗑", accent_color=COLOR_ERROR)
        self.card_deleted.pack(side='left', fill='both', expand=True, padx=5)

        self.card_last_id = StatCard(stats_frame, "Último ID", "0", icon="⚡", accent_color=COLOR_INFO)
        self.card_last_id.pack(side='left', fill='both', expand=True, padx=(10, 0))

        # Sección dividida: Acciones Rápidas & Estado del Sistema
        mid_row = tk.Frame(self, bg=BG_BASE)
        mid_row.pack(fill='x', padx=24, pady=(0, 20))

        # Acciones Rápidas
        actions_card = GlassCard(mid_row, title="Acciones Rápidas", subtitle="Operaciones comunes del sistema")
        actions_card.pack(side='left', fill='both', expand=True, padx=(0, 10))

        btns_box = tk.Frame(actions_card.content, bg=BG_CARD)
        btns_box.pack(fill='x', pady=8)

        btn1 = GlassButton(btns_box, text="Nuevo Contacto", icon="➕", variant='primary',
                           command=lambda: self._navigate('contacts_add'))
        btn1.pack(side='left', padx=(0, 8))

        btn2 = GlassButton(btns_box, text="Ver Directorio", icon="👥", variant='secondary',
                           command=lambda: self._navigate('contacts'))
        btn2.pack(side='left', padx=(0, 8))

        btn3 = GlassButton(btns_box, text="Exportar PDF", icon="📊", variant='secondary',
                           command=lambda: self._navigate('export'))
        btn3.pack(side='left', padx=(0, 8))

        btn4 = GlassButton(btns_box, text="Herramientas", icon="🔧", variant='secondary',
                           command=lambda: self._navigate('tools'))
        btn4.pack(side='left')

        # Estado del Sistema / Integridad
        self.status_card = GlassCard(mid_row, title="Integridad del Archivo", subtitle="Criptografía SHA-256")
        self.status_card.pack(side='right', fill='both', expand=True, padx=(10, 0))

        self.lbl_hash_status = tk.Label(
            self.status_card.content, text="Verificando integridad...", font=FONT_BODY,
            fg=TEXT_SECONDARY, bg=BG_CARD, anchor='w'
        )
        self.lbl_hash_status.pack(fill='x', pady=4)

        self.lbl_file_size = tk.Label(
            self.status_card.content, text="Tamaño de datos: Calculando...", font=FONT_SMALL,
            fg=TEXT_MUTED, bg=BG_CARD, anchor='w'
        )
        self.lbl_file_size.pack(fill='x')

        # Tabla de Contactos Recientes
        table_card = GlassCard(self, title="Contactos Recientes en Archivo", subtitle="Últimos registros leídos mediante acceso aleatorio")
        table_card.pack(fill='both', expand=True, padx=24, pady=(0, 20))

        cols = ['id', 'nombre', 'telefono', 'correo', 'ciudad']
        heads = ['ID', 'Nombre', 'Teléfono', 'Correo', 'Ciudad']
        widths = [60, 200, 130, 200, 130]

        self.recent_table = GlassTable(table_card.content, columns=cols, headings=heads, widths=widths)
        self.recent_table.pack(fill='both', expand=True)

    def _navigate(self, target: str):
        if self.on_navigate:
            self.on_navigate(target)

    def refresh(self):
        """Actualiza todas las métricas y la tabla."""
        stats = self.service.get_stats()
        self.card_total.set_value(str(stats.get('total', 0)))
        self.card_active.set_value(str(stats.get('active', 0)))
        self.card_deleted.set_value(str(stats.get('deleted', 0)))
        self.card_last_id.set_value(str(stats.get('last_id') or 'N/A'))

        # Integridad
        ok, msg = self.service.verify_integrity()
        color = COLOR_SUCCESS if ok else COLOR_ERROR
        prefix = "✓ Integridad verificada: Hash coincide" if ok else "⚠ ALERTA: Archivo modificado externamente"
        self.lbl_hash_status.configure(text=prefix, fg=color)

        # Archivo
        finfo = self.service.get_file_info()
        self.lbl_file_size.configure(
            text=f"Archivo físico: {finfo.get('size', 0)} bytes ({finfo.get('total_records', 0)} registros × 256B)"
        )

        # Cargar últimos 5 contactos
        all_contacts = self.service.get_all_contacts(include_deleted=False)
        recent = all_contacts[-5:] if len(all_contacts) > 5 else all_contacts
        self.recent_table.load_data(recent)

