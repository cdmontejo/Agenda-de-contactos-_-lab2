# -*- coding: utf-8 -*-
"""
Formulario modal para Agregar / Modificar Contactos con efecto Liquid Glass.

Incluye validación en tiempo real y retroalimentación visual clara.
"""

import tkinter as tk
import logging

from ui.theme import (
    BG_BASE, BG_CARD, BORDER_GLASS, TEXT_PRIMARY, TEXT_SECONDARY,
    FONT_HEADING_SM, FONT_SMALL
)
from ui.components import GlassEntry, GlassButton, Toast
from services.validators import (
    validate_id, validate_name, validate_phone, validate_email, validate_city
)

logger = logging.getLogger(__name__)


class ContactForm(tk.Toplevel):
    """
    Ventana modal para crear o editar contactos.
    """

    def __init__(self, parent, contact_service, contact_data: dict = None,
                 on_success=None):
        super().__init__(parent)
        self.service = contact_service
        self.contact_data = contact_data
        self.is_edit = contact_data is not None
        self.on_success = on_success

        title_text = "Modificar Contacto" if self.is_edit else "Nuevo Contacto"
        self.title(title_text)
        self.geometry("460x520")
        self.configure(bg=BG_BASE)
        self.resizable(False, False)
        self.transient(parent)
        self.grab_set()

        # Centrar en pantalla
        self.update_idletasks()
        try:
            px = parent.winfo_rootx()
            py = parent.winfo_rooty()
            pw = parent.winfo_width()
            ph = parent.winfo_height()
            x = px + (pw - 460) // 2
            y = py + (ph - 520) // 2
            self.geometry(f"+{x}+{y}")
        except Exception:
            pass

        # Borde de cristal
        self.border = tk.Frame(self, bg=BORDER_GLASS, padx=1, pady=1)
        self.border.pack(fill='both', expand=True, padx=16, pady=16)

        self.container = tk.Frame(self.border, bg=BG_CARD, padx=24, pady=20)
        self.container.pack(fill='both', expand=True)

        # Encabezado
        h_lbl = tk.Label(
            self.container, text=title_text, font=FONT_HEADING_SM,
            fg=TEXT_PRIMARY, bg=BG_CARD, anchor='w'
        )
        h_lbl.pack(fill='x', pady=(0, 4))

        sub_text = (
            f"Modificando registro ID #{contact_data.get('id')}"
            if self.is_edit else
            "Ingrese los datos del nuevo contacto (256 bytes fijos UTF-8)"
        )
        s_lbl = tk.Label(
            self.container, text=sub_text, font=FONT_SMALL,
            fg=TEXT_SECONDARY, bg=BG_CARD, anchor='w'
        )
        s_lbl.pack(fill='x', pady=(0, 16))

        # Campos
        self.entry_id = GlassEntry(self.container, label="ID de Contacto (Único):")
        self.entry_id.pack(fill='x', pady=(0, 8))

        self.entry_nombre = GlassEntry(self.container, label="Nombre Completo:")
        self.entry_nombre.pack(fill='x', pady=(0, 8))

        self.entry_telefono = GlassEntry(self.container, label="Teléfono:")
        self.entry_telefono.pack(fill='x', pady=(0, 8))

        self.entry_correo = GlassEntry(self.container, label="Correo Electrónico:")
        self.entry_correo.pack(fill='x', pady=(0, 8))

        self.entry_ciudad = GlassEntry(self.container, label="Ciudad:")
        self.entry_ciudad.pack(fill='x', pady=(0, 16))

        # Rellenar si es edición
        if self.is_edit:
            self.entry_id.set(contact_data.get('id', ''))
            self.entry_id.entry.configure(state='disabled')
            self.entry_nombre.set(contact_data.get('nombre', ''))
            self.entry_telefono.set(contact_data.get('telefono', ''))
            self.entry_correo.set(contact_data.get('correo', ''))
            self.entry_ciudad.set(contact_data.get('ciudad', ''))
        else:
            # Sugerir siguiente ID
            stats = self.service.get_stats()
            next_id = (stats.get('last_id') or 0) + 1
            self.entry_id.set(str(next_id))

        # Botones
        btn_box = tk.Frame(self.container, bg=BG_CARD)
        btn_box.pack(fill='x', pady=(8, 0))

        cancel_btn = GlassButton(
            btn_box, text="Cancelar", variant='secondary',
            width=110, command=self.destroy
        )
        cancel_btn.pack(side='right', padx=(8, 0))

        save_btn = GlassButton(
            btn_box, text="Guardar Registro", variant='primary',
            width=150, command=self._save
        )
        save_btn.pack(side='right')

    def _validate(self) -> bool:
        has_error = False

        # Validar ID
        if not self.is_edit:
            ok, err = validate_id(self.entry_id.get())
            if not ok:
                self.entry_id.set_error(err)
                has_error = True
            else:
                self.entry_id.clear_error()

        # Validar Nombre
        ok, err = validate_name(self.entry_nombre.get())
        if not ok:
            self.entry_nombre.set_error(err)
            has_error = True
        else:
            self.entry_nombre.clear_error()

        # Validar Teléfono
        ok, err = validate_phone(self.entry_telefono.get())
        if not ok:
            self.entry_telefono.set_error(err)
            has_error = True
        else:
            self.entry_telefono.clear_error()

        # Validar Correo
        ok, err = validate_email(self.entry_correo.get())
        if not ok:
            self.entry_correo.set_error(err)
            has_error = True
        else:
            self.entry_correo.clear_error()

        # Validar Ciudad
        ok, err = validate_city(self.entry_ciudad.get())
        if not ok:
            self.entry_ciudad.set_error(err)
            has_error = True
        else:
            self.entry_ciudad.clear_error()

        return not has_error

    def _save(self):
        if not self._validate():
            return

        cid = int(self.entry_id.get())
        data = {
            'id': cid,
            'nombre': self.entry_nombre.get(),
            'telefono': self.entry_telefono.get(),
            'correo': self.entry_correo.get(),
            'ciudad': self.entry_ciudad.get()
        }

        if self.is_edit:
            ok, msg = self.service.update_contact(cid, data)
        else:
            ok, msg = self.service.add_contact(data)

        if ok:
            Toast(self.master, msg, toast_type='success')
            if self.on_success:
                self.on_success()
            self.destroy()
        else:
            Toast(self, msg, toast_type='error')

