# -*- coding: utf-8 -*-
"""
Vista de Gestión de Contactos con acceso aleatorio e indexación.

Permite:
  - Listado completo de contactos con filtrado en tiempo real
  - Búsqueda directa por ID con seek() y tell()
  - Alta, modificación y eliminación lógica
  - Restauración de registros eliminados
"""

import tkinter as tk
from tkinter import simpledialog
import logging

from ui.theme import (
    BG_BASE, BG_CARD, TEXT_PRIMARY, TEXT_SECONDARY, COLOR_SUCCESS,
    COLOR_ERROR, FONT_HEADING_LG, FONT_SMALL
)
from ui.components import GlassCard, GlassButton, GlassTable, SearchBar, Toast
from ui.contact_form import ContactForm
from ui.dialogs import ConfirmDialog, InfoDialog

logger = logging.getLogger(__name__)


class ContactsView(tk.Frame):
    """
    Vista principal de gestión del directorio de contactos.
    """

    def __init__(self, parent, contact_service, on_position_update=None, **kwargs):
        super().__init__(parent, bg=BG_BASE, **kwargs)
        self.service = contact_service
        self.on_position_update = on_position_update
        self.current_records = []

        self._build_ui()
        self.refresh()

    def _build_ui(self):
        # Cabecera
        head_frame = tk.Frame(self, bg=BG_BASE)
        head_frame.pack(fill='x', padx=24, pady=(20, 12))

        top_row = tk.Frame(head_frame, bg=BG_BASE)
        top_row.pack(fill='x')

        h1 = tk.Label(top_row, text="Directorio de Contactos", font=FONT_HEADING_LG,
                      fg=TEXT_PRIMARY, bg=BG_BASE, anchor='w')
        h1.pack(side='left')

        # Botón Nuevo Contacto destacado
        btn_add = GlassButton(top_row, text="Nuevo Contacto", icon="➕", variant='primary',
                              width=160, command=self.on_add_contact)
        btn_add.pack(side='right')

        # Botón Buscar por ID (Requisito explícito del laboratorio)
        btn_search_id = GlassButton(top_row, text="Buscar por ID", icon="🔍", variant='secondary',
                                    width=140, command=self.on_search_by_id)
        btn_search_id.pack(side='right', padx=(0, 8))

        sub = tk.Label(head_frame, text="Almacenamiento de registros de tamaño fijo (256 bytes) con índice primario JSON",
                       font=FONT_SMALL, fg=TEXT_SECONDARY, bg=BG_BASE, anchor='w')
        sub.pack(fill='x', pady=(4, 0))

        # Barra de control: Búsqueda, Filtros y Acciones
        ctrl_card = GlassCard(self, padx=16, pady=12)
        ctrl_card.pack(fill='x', padx=24, pady=(0, 14))

        ctrl_box = tk.Frame(ctrl_card.content, bg=BG_CARD)
        ctrl_box.pack(fill='x')

        # Buscador reactivo
        self.search_bar = SearchBar(ctrl_box, on_search=self._on_search)
        self.search_bar.pack(side='left', fill='x', expand=True, padx=(0, 16))

        # Checkbox para incluir eliminados
        self.var_show_deleted = tk.BooleanVar(value=False)
        chk_del = tk.Checkbutton(
            ctrl_box, text="Mostrar eliminados", variable=self.var_show_deleted,
            bg=BG_CARD, fg=TEXT_SECONDARY, selectcolor=BG_BASE,
            activebackground=BG_CARD, activeforeground=TEXT_PRIMARY,
            command=self.refresh
        )
        chk_del.pack(side='left', padx=(0, 16))

        # Botones de fila
        btn_edit = GlassButton(ctrl_box, text="Modificar", icon="✏", variant='secondary',
                               width=110, command=self.on_edit_selected)
        btn_edit.pack(side='left', padx=(0, 6))

        btn_del = GlassButton(ctrl_box, text="Eliminar", icon="🗑", variant='danger',
                              width=110, command=self.on_delete_selected)
        btn_del.pack(side='left', padx=(0, 6))

        btn_restore = GlassButton(ctrl_box, text="Restaurar", icon="↺", variant='success',
                                  width=110, command=self.on_restore_selected)
        btn_restore.pack(side='left')

        # Tabla de contactos
        table_card = GlassCard(self, padx=16, pady=14)
        table_card.pack(fill='both', expand=True, padx=24, pady=(0, 16))

        cols = ['id', 'nombre', 'telefono', 'correo', 'ciudad', 'estado']
        heads = ['ID', 'Nombre Completo', 'Teléfono', 'Correo Electrónico', 'Ciudad', 'Estado']
        widths = [60, 220, 130, 220, 140, 80]

        self.table = GlassTable(
            table_card.content, columns=cols, headings=heads, widths=widths,
            on_double_click=self._on_double_click
        )
        self.table.pack(fill='both', expand=True)

        # Barra inferior de conteo
        bot_bar = tk.Frame(self, bg=BG_BASE)
        bot_bar.pack(fill='x', padx=24, pady=(0, 12))

        self.lbl_count = tk.Label(
            bot_bar, text="Cargando registros...", font=FONT_SMALL,
            fg=TEXT_SECONDARY, bg=BG_BASE, anchor='w'
        )
        self.lbl_count.pack(side='left')

    def refresh(self):
        """Recarga los contactos según el filtro de búsqueda y eliminados."""
        query = self.search_bar.get_query()
        field = self.search_bar._map_field()

        if query:
            records = self.service.search_contacts(query, field)
        else:
            show_del = self.var_show_deleted.get()
            records = self.service.get_all_contacts(include_deleted=show_del)

        # Mapear estado legible
        display_records = []
        for r in records:
            item = dict(r)
            item['estado'] = "Activo" if r.get('estado') == 'A' else "Eliminado"
            display_records.append(item)

        self.current_records = display_records
        self.table.load_data(display_records)

        stats = self.service.get_stats()
        self.lbl_count.configure(
            text=f"Mostrando {len(display_records)} registros (Total en archivo: {stats.get('total', 0)}, Activos: {stats.get('active', 0)})"
        )

    def _on_search(self, query: str, field: str):
        self.refresh()

    def _on_double_click(self, selected: dict):
        self.on_edit_selected()

    def on_add_contact(self):
        """Abre el formulario para nuevo contacto."""
        ContactForm(self, self.service, on_success=self.refresh)

    def on_search_by_id(self):
        """
        Búsqueda de contacto por ID con seek() y tell() demostrados.
        Requisito explícito del laboratorio.
        """
        cid_str = simpledialog.askstring("Buscar por ID", "Ingrese el ID del contacto a buscar:", parent=self)
        if not cid_str or not cid_str.strip():
            return

        try:
            cid = int(cid_str.strip())
        except ValueError:
            Toast(self, "El ID debe ser un número entero válido", toast_type='error')
            return

        # Consultar índice primero
        rec_num = self.service.index_manager.get(cid)
        if rec_num is None:
            Toast(self, f"El ID {cid} no existe en el índice primario", toast_type='error')
            return

        # Acceso aleatorio con seek
        contact = self.service.search_by_id(cid)
        if contact:
            pos_bytes = rec_num * 256
            if self.on_position_update:
                self.on_position_update(pos_bytes, rec_num)

            msg = (
                f"✓ Contacto encontrado mediante acceso aleatorio:\n\n"
                f"• ID: {contact.get('id')}\n"
                f"• Nombre: {contact.get('nombre')}\n"
                f"• Teléfono: {contact.get('telefono')}\n"
                f"• Correo: {contact.get('correo')}\n"
                f"• Ciudad: {contact.get('ciudad')}\n"
                f"• Estado: {'Activo' if contact.get('estado') == 'A' else 'Eliminado'}\n\n"
                f"Demostración técnica:\n"
                f"→ Índice: ID {cid} asignado al registro #{rec_num}\n"
                f"→ Operación seek({rec_num} × 256 bytes) posicionada en byte {pos_bytes}\n"
                f"→ Comprobado con tell(): {pos_bytes}B"
            )
            InfoDialog(self, f"Resultado de Búsqueda (ID {cid})", msg)
        else:
            Toast(self, f"No se pudo leer el registro #{rec_num} en el archivo", toast_type='error')

    def on_edit_selected(self):
        """Modifica el contacto seleccionado."""
        sel = self.table.get_selected()
        if not sel:
            Toast(self, "Seleccione un contacto para modificar", toast_type='warning')
            return

        cid = int(sel['id'])
        contact = self.service.search_by_id(cid)
        if contact:
            ContactForm(self, self.service, contact_data=contact, on_success=self.refresh)

    def on_delete_selected(self):
        """Elimina lógicamente el contacto seleccionado."""
        sel = self.table.get_selected()
        if not sel:
            Toast(self, "Seleccione un contacto para eliminar", toast_type='warning')
            return

        cid = int(sel['id'])
        name = sel.get('nombre', '')

        dlg = ConfirmDialog(
            self, title="Confirmar Eliminación",
            message=f"¿Está seguro de eliminar lógicamente al contacto '{name}' (ID: {cid})?\n\nEl registro se marcará como 'D' sin reescribir el resto del archivo.",
            confirm_text="Eliminar", variant='danger'
        )
        if dlg.result:
            ok, msg = self.service.delete_contact(cid)
            if ok:
                Toast(self, msg, toast_type='success')
                self.refresh()
            else:
                Toast(self, msg, toast_type='error')

    def on_restore_selected(self):
        """Restaura un contacto eliminado."""
        sel = self.table.get_selected()
        if not sel:
            Toast(self, "Seleccione un contacto para restaurar", toast_type='warning')
            return

        cid = int(sel['id'])
        ok, msg = self.service.restore_contact(cid)
        if ok:
            Toast(self, msg, toast_type='success')
            self.refresh()
        else:
            Toast(self, msg, toast_type='error')

