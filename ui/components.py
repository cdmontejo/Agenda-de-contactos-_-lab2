# -*- coding: utf-8 -*-
"""
Componentes de interfaz gráfica con diseño Liquid Glass.

Proporciona widgets personalizados y reutilizables inspirados en
la estética de iOS / macOS:
  - GlassCard: Tarjetas con fondo de cristal y bordes sutiles
  - GlassButton: Botones interactivos con efectos hover y variantes
  - GlassEntry: Campos de texto con validación y estados visuales
  - GlassTable: Tabla ttk estilizada con scrollbars y selección
  - StatCard: Tarjetas de estadísticas para el Dashboard
  - SearchBar: Barra de búsqueda con debounce y selector de campo
  - Toast: Notificaciones flotantes animadas
  - StatusBar: Barra inferior de estado con posición tell()
"""

import tkinter as tk
from tkinter import ttk
import logging

from ui.theme import (
    BG_BASE, BG_GLASS, BG_GLASS_HOVER, BG_CARD, BG_INPUT,
    BG_TABLE_HEADER, BORDER_GLASS, BORDER_INPUT, BORDER_FOCUS,
    TEXT_PRIMARY, TEXT_SECONDARY, TEXT_MUTED, ACCENT_PRIMARY,
    ACCENT_HOVER, ACCENT_GLOW, COLOR_SUCCESS, COLOR_WARNING,
    COLOR_ERROR, COLOR_INFO, BTN_PRIMARY_BG, BTN_PRIMARY_HOVER,
    BTN_SECONDARY_BG, BTN_SECONDARY_HOVER, BTN_SUCCESS_BG,
    BTN_SUCCESS_HOVER, BTN_DANGER_BG, BTN_DANGER_HOVER,
    FONT_FAMILY, FONT_HEADING_SM, FONT_BODY, FONT_BODY_BOLD,
    FONT_SMALL, FONT_SMALL_BOLD, FONT_TINY, FONT_MONO,
    PAD_CARD, PAD_ELEMENT, PAD_SMALL, BUTTON_HEIGHT, ENTRY_HEIGHT,
    TABLE_ROW_HOVER, TABLE_ROW_ALT
)

logger = logging.getLogger(__name__)


class GlassCard(tk.Frame):
    """
    Tarjeta contenedora con fondo de cristal y borde sutil.
    Opcionalmente puede incluir un título y un subtítulo.
    """

    def __init__(self, parent, title: str = "", subtitle: str = "",
                 bg_color: str = BG_CARD, border_color: str = BORDER_GLASS,
                 padx: int = PAD_CARD, pady: int = PAD_CARD, **kwargs):
        super().__init__(parent, bg=border_color, **kwargs)
        self.padx = padx
        self.pady = pady

        # Contenedor interior para simular el borde de 1px
        self.inner = tk.Frame(self, bg=bg_color)
        self.inner.pack(fill='both', expand=True, padx=1, pady=1)

        # Header opcional
        if title or subtitle:
            self.header_frame = tk.Frame(self.inner, bg=bg_color)
            self.header_frame.pack(fill='x', padx=padx, pt=pady if not subtitle else 0,
                                   pady=(pady, PAD_SMALL))

            if title:
                self.title_lbl = tk.Label(
                    self.header_frame, text=title, font=FONT_HEADING_SM,
                    fg=TEXT_PRIMARY, bg=bg_color, anchor='w'
                )
                self.title_lbl.pack(fill='x')

            if subtitle:
                self.sub_lbl = tk.Label(
                    self.header_frame, text=subtitle, font=FONT_SMALL,
                    fg=TEXT_SECONDARY, bg=bg_color, anchor='w'
                )
                self.sub_lbl.pack(fill='x', pady=(2, 0))

        # Contenedor para el contenido del cliente
        self.content = tk.Frame(self.inner, bg=bg_color)
        self.content.pack(fill='both', expand=True, padx=padx, pady=pady)


class GlassButton(tk.Canvas):
    """
    Botón interactivo dibujado en Canvas para control visual total.
    Soporta esquinas redondeadas, estados hover, variantes y clic.
    """

    VARIANTS = {
        'primary': {
            'bg': BTN_PRIMARY_BG,
            'hover': BTN_PRIMARY_HOVER,
            'fg': '#ffffff',
            'border': ACCENT_GLOW
        },
        'secondary': {
            'bg': BTN_SECONDARY_BG,
            'hover': BTN_SECONDARY_HOVER,
            'fg': TEXT_PRIMARY,
            'border': BORDER_GLASS
        },
        'success': {
            'bg': BTN_SUCCESS_BG,
            'hover': BTN_SUCCESS_HOVER,
            'fg': '#ffffff',
            'border': COLOR_SUCCESS
        },
        'danger': {
            'bg': BTN_DANGER_BG,
            'hover': BTN_DANGER_HOVER,
            'fg': '#ffffff',
            'border': COLOR_ERROR
        },
        'info': {
            'bg': '#2563eb',
            'hover': '#1d4ed8',
            'fg': '#ffffff',
            'border': COLOR_INFO
        }
    }

    def __init__(self, parent, text: str = "", command=None,
                 variant: str = 'primary', width: int = 140,
                 height: int = BUTTON_HEIGHT, radius: int = 8,
                 icon: str = "", font=FONT_BODY_BOLD, **kwargs):
        super().__init__(parent, width=width, height=height,
                         bg=parent.cget('bg'), highlightthickness=0, **kwargs)

        self.text = f"{icon}  {text}".strip() if icon else text
        self.command = command
        self.variant = variant
        self.cfg = self.VARIANTS.get(variant, self.VARIANTS['primary'])
        self.btn_width = width
        self.btn_height = height
        self.radius = radius
        self.font = font
        self.enabled = True
        self.is_hovered = False

        self._draw(self.cfg['bg'])

        self.bind('<Enter>', self._on_enter)
        self.bind('<Leave>', self._on_leave)
        self.bind('<Button-1>', self._on_click)

    def _draw_rounded_rect(self, x1, y1, x2, y2, r, fill, outline):
        points = [
            x1 + r, y1,
            x2 - r, y1,
            x2, y1,
            x2, y1 + r,
            x2, y2 - r,
            x2, y2,
            x2 - r, y2,
            x1 + r, y2,
            x1, y2,
            x1, y2 - r,
            x1, y1 + r,
            x1, y1
        ]
        return self.create_polygon(points, smooth=True, fill=fill, outline=outline, width=1)

    def _draw(self, fill_color):
        self.delete('all')
        # Dibujar forma redondeada
        border_col = self.cfg['border'] if self.is_hovered else BORDER_GLASS
        self._draw_rounded_rect(2, 2, self.btn_width - 2, self.btn_height - 2,
                                self.radius, fill_color, border_col)
        # Dibujar texto centrado
        text_fg = self.cfg['fg'] if self.enabled else TEXT_MUTED
        self.create_text(
            self.btn_width / 2, self.btn_height / 2,
            text=self.text, fill=text_fg, font=self.font
        )

    def _on_enter(self, _event):
        if not self.enabled:
            return
        self.is_hovered = True
        self._draw(self.cfg['hover'])
        self.config(cursor='hand2')

    def _on_leave(self, _event):
        if not self.enabled:
            return
        self.is_hovered = False
        self._draw(self.cfg['bg'])
        self.config(cursor='')

    def _on_click(self, _event):
        if self.enabled and self.command:
            self.command()

    def set_enabled(self, enabled: bool):
        self.enabled = enabled
        fill = self.cfg['bg'] if enabled else BG_BASE
        self._draw(fill)


class GlassEntry(tk.Frame):
    """
    Campo de texto estilizado con etiqueta, borde con foco activo
    y etiqueta de error en tiempo real.
    """

    def __init__(self, parent, label: str = "", placeholder: str = "",
                 show: str = "", width: int = 30, **kwargs):
        super().__init__(parent, bg=parent.cget('bg'), **kwargs)
        self.placeholder = placeholder
        self.has_placeholder = False

        # Etiqueta superior
        if label:
            self.lbl = tk.Label(
                self, text=label, font=FONT_SMALL_BOLD,
                fg=TEXT_SECONDARY, bg=parent.cget('bg'), anchor='w'
            )
            self.lbl.pack(fill='x', pady=(0, 4))

        # Marco del borde
        self.border_frame = tk.Frame(self, bg=BORDER_INPUT, padx=1, pady=1)
        self.border_frame.pack(fill='x')

        # Entry interior
        self.entry = tk.Entry(
            self.border_frame, bg=BG_INPUT, fg=TEXT_PRIMARY,
            insertbackground=TEXT_PRIMARY, relief='flat',
            font=FONT_BODY, show=show, width=width
        )
        self.entry.pack(fill='both', expand=True, ipady=6, padx=8, pady=2)

        # Etiqueta de mensaje de error
        self.err_lbl = tk.Label(
            self, text="", font=FONT_TINY, fg=COLOR_ERROR,
            bg=parent.cget('bg'), anchor='w'
        )
        self.err_lbl.pack(fill='x', pady=(2, 0))

        # Eventos de foco
        self.entry.bind('<FocusIn>', self._on_focus_in)
        self.entry.bind('<FocusOut>', self._on_focus_out)

    def _on_focus_in(self, _event):
        self.border_frame.configure(bg=BORDER_FOCUS)

    def _on_focus_out(self, _event):
        if not self.err_lbl.cget('text'):
            self.border_frame.configure(bg=BORDER_INPUT)

    def get(self) -> str:
        return self.entry.get().strip()

    def set(self, text: str):
        self.entry.delete(0, tk.END)
        self.entry.insert(0, str(text))
        self.clear_error()

    def set_error(self, message: str):
        self.err_lbl.configure(text=message)
        self.border_frame.configure(bg=COLOR_ERROR)

    def clear_error(self):
        self.err_lbl.configure(text="")
        self.border_frame.configure(bg=BORDER_INPUT)


class StatCard(tk.Frame):
    """
    Tarjeta de estadística para Dashboard con métrica, ícono y título.
    """

    def __init__(self, parent, title: str, value: str, icon: str = "📊",
                 accent_color: str = ACCENT_PRIMARY, **kwargs):
        super().__init__(parent, bg=BORDER_GLASS, padx=1, pady=1, **kwargs)

        self.inner = tk.Frame(self, bg=BG_CARD, padx=18, pady=16)
        self.inner.pack(fill='both', expand=True)

        top_row = tk.Frame(self.inner, bg=BG_CARD)
        top_row.pack(fill='x')

        self.icon_lbl = tk.Label(
            top_row, text=icon, font=(FONT_FAMILY, 20),
            fg=accent_color, bg=BG_CARD
        )
        self.icon_lbl.pack(side='left')

        self.val_lbl = tk.Label(
            self.inner, text=value, font=(FONT_FAMILY, 24, 'bold'),
            fg=TEXT_PRIMARY, bg=BG_CARD, anchor='w'
        )
        self.val_lbl.pack(fill='x', pady=(8, 2))

        self.title_lbl = tk.Label(
            self.inner, text=title.upper(), font=FONT_TINY,
            fg=TEXT_SECONDARY, bg=BG_CARD, anchor='w'
        )
        self.title_lbl.pack(fill='x')

    def set_value(self, new_value: str):
        self.val_lbl.configure(text=str(new_value))


class SearchBar(tk.Frame):
    """
    Barra de búsqueda con selector de campo y callback reactivo.
    """

    def __init__(self, parent, on_search=None, **kwargs):
        super().__init__(parent, bg=parent.cget('bg'), **kwargs)
        self.on_search = on_search

        # Selector de campo
        self.field_var = tk.StringVar(value='all')
        self.combo = ttk.Combobox(
            self, textvariable=self.field_var, state='readonly',
            values=['Todos', 'Nombre', 'Teléfono', 'Correo', 'Ciudad'],
            width=10, font=FONT_SMALL
        )
        self.combo.set('Todos')
        self.combo.pack(side='left', padx=(0, 8), ipady=3)
        self.combo.bind('<<ComboboxSelected>>', self._trigger_search)

        # Entrada de texto
        self.entry_border = tk.Frame(self, bg=BORDER_INPUT, padx=1, pady=1)
        self.entry_border.pack(side='left', fill='x', expand=True)

        self.search_entry = tk.Entry(
            self.entry_border, bg=BG_INPUT, fg=TEXT_PRIMARY,
            insertbackground=TEXT_PRIMARY, relief='flat',
            font=FONT_BODY
        )
        self.search_entry.pack(fill='both', expand=True, ipady=5, padx=8)
        self.search_entry.bind('<KeyRelease>', self._trigger_search)
        self.search_entry.bind('<FocusIn>', lambda e: self.entry_border.config(bg=BORDER_FOCUS))
        self.search_entry.bind('<FocusOut>', lambda e: self.entry_border.config(bg=BORDER_INPUT))

        # Botón limpiar
        self.clear_btn = tk.Button(
            self, text="✕", font=FONT_SMALL_BOLD, fg=TEXT_MUTED,
            bg=BG_INPUT, activebackground=BG_GLASS_HOVER,
            activeforeground=TEXT_PRIMARY, relief='flat',
            command=self.clear, cursor='hand2'
        )
        self.clear_btn.pack(side='left', padx=(6, 0), ipadx=4, ipady=2)

    def _map_field(self) -> str:
        mapping = {
            'Todos': 'all',
            'Nombre': 'nombre',
            'Teléfono': 'telefono',
            'Correo': 'correo',
            'Ciudad': 'ciudad'
        }
        return mapping.get(self.combo.get(), 'all')

    def _trigger_search(self, _event=None):
        if self.on_search:
            query = self.search_entry.get().strip()
            field = self._map_field()
            self.on_search(query, field)

    def get_query(self) -> str:
        return self.search_entry.get().strip()

    def clear(self):
        self.search_entry.delete(0, tk.END)
        self._trigger_search()


class GlassTable(tk.Frame):
    """
    Tabla interactiva usando Treeview con estética Liquid Glass,
    filas alternadas, hover y eventos de selección.
    """

    def __init__(self, parent, columns: list, headings: list,
                 widths: list = None, on_select=None, on_double_click=None, **kwargs):
        super().__init__(parent, bg=BORDER_GLASS, padx=1, pady=1, **kwargs)

        self.columns = columns
        self.headings = headings
        self.on_select = on_select
        self.on_double_click = on_double_click

        container = tk.Frame(self, bg=BG_GLASS)
        container.pack(fill='both', expand=True)

        # Configurar Treeview
        self.tree = ttk.Treeview(
            container, columns=columns, show='headings',
            selectmode='browse'
        )

        for i, col in enumerate(columns):
            heading = headings[i] if i < len(headings) else col
            width = widths[i] if widths and i < len(widths) else 120
            self.tree.heading(col, text=heading, anchor='w')
            self.tree.column(col, width=width, anchor='w', minwidth=60)

        # Scrollbars
        vsb = ttk.Scrollbar(container, orient='vertical', command=self.tree.yview)
        hsb = ttk.Scrollbar(container, orient='horizontal', command=self.tree.xview)
        self.tree.configure(yscrollcommand=vsb.set, xscrollcommand=hsb.set)

        self.tree.grid(row=0, column=0, sticky='nsew')
        vsb.grid(row=0, column=1, sticky='ns')
        hsb.grid(row=1, column=0, sticky='ew')

        container.grid_rowconfigure(0, weight=1)
        container.grid_columnconfigure(0, weight=1)

        # Configurar tags de color
        self.tree.tag_configure('even', background=BG_CARD, foreground=TEXT_PRIMARY)
        self.tree.tag_configure('odd', background=TABLE_ROW_ALT, foreground=TEXT_PRIMARY)
        self.tree.tag_configure('deleted', background='#2c171d', foreground='#f87171')

        # Eventos
        self.tree.bind('<<TreeviewSelect>>', self._handle_select)
        if on_double_click:
            self.tree.bind('<Double-1>', self._handle_double_click)

    def _handle_select(self, _event):
        if self.on_select:
            selected = self.get_selected()
            if selected:
                self.on_select(selected)

    def _handle_double_click(self, _event):
        if self.on_double_click:
            selected = self.get_selected()
            if selected:
                self.on_double_click(selected)

    def load_data(self, records: list):
        """Carga una lista de diccionarios en la tabla."""
        self.clear()
        for idx, rec in enumerate(records):
            values = [rec.get(col, '') for col in self.columns]
            estado = rec.get('estado', 'A')
            tag = 'deleted' if estado == 'D' else ('even' if idx % 2 == 0 else 'odd')
            self.tree.insert('', 'end', iid=str(rec.get('id', idx)), values=values, tags=(tag,))

    def clear(self):
        for item in self.tree.get_children():
            self.tree.delete(item)

    def get_selected(self) -> dict | None:
        selection = self.tree.selection()
        if not selection:
            return None
        item_id = selection[0]
        values = self.tree.item(item_id, 'values')
        return dict(zip(self.columns, values))


class StatusBar(tk.Frame):
    """
    Barra de estado inferior que muestra la posición física del archivo (tell)
    y el total de registros en tiempo real.
    """

    def __init__(self, parent, **kwargs):
        super().__init__(parent, bg=BG_BASE, height=32, **kwargs)

        self.status_lbl = tk.Label(
            self, text="● Sistema listo", font=FONT_SMALL,
            fg=TEXT_SECONDARY, bg=BG_BASE, anchor='w'
        )
        self.status_lbl.pack(side='left', padx=16, pady=4)

        self.tell_lbl = tk.Label(
            self, text="seek() / tell(): posición 0B", font=FONT_MONO,
            fg=ACCENT_GLOW, bg=BG_BASE, anchor='e'
        )
        self.tell_lbl.pack(side='right', padx=16, pady=4)

    def set_status(self, text: str, is_error: bool = False):
        color = COLOR_ERROR if is_error else TEXT_SECONDARY
        icon = "⚠" if is_error else "●"
        self.status_lbl.configure(text=f"{icon} {text}", fg=color)

    def set_position_info(self, position_bytes: int, record_num: int = None):
        if record_num is not None:
            txt = f"seek({record_num} * 256B) -> tell() = {position_bytes}B [Registro #{record_num}]"
        else:
            txt = f"tell() = {position_bytes}B"
        self.tell_lbl.configure(text=txt)


class Toast(tk.Toplevel):
    """
    Notificación flotante no invasiva tipo iOS Toast.
    Se auto-destruye después de unos segundos.
    """

    def __init__(self, parent, message: str, toast_type: str = 'info',
                 duration_ms: int = 3500):
        super().__init__(parent)
        self.overrideredirect(True)
        self.attributes('-topmost', True)

        colors = {
            'success': (COLOR_SUCCESS, '✓ Éxito'),
            'error': (COLOR_ERROR, '✕ Error'),
            'warning': (COLOR_WARNING, '⚠ Advertencia'),
            'info': (COLOR_INFO, 'ℹ Información')
        }
        accent, title = colors.get(toast_type, (COLOR_INFO, 'ℹ Info'))

        border = tk.Frame(self, bg=accent, padx=1, pady=1)
        border.pack(fill='both', expand=True)

        inner = tk.Frame(border, bg='#1a1a2e', padx=16, pady=10)
        inner.pack(fill='both', expand=True)

        t_lbl = tk.Label(inner, text=title, font=FONT_SMALL_BOLD, fg=accent, bg='#1a1a2e', anchor='w')
        t_lbl.pack(fill='x')

        m_lbl = tk.Label(inner, text=message, font=FONT_BODY, fg=TEXT_PRIMARY, bg='#1a1a2e', anchor='w')
        m_lbl.pack(fill='x', pady=(4, 0))

        # Posicionar en la esquina superior derecha del padre
        self.update_idletasks()
        try:
            px = parent.winfo_rootx()
            py = parent.winfo_rooty()
            pw = parent.winfo_width()
            x = px + pw - self.winfo_width() - 24
            y = py + 36
            self.geometry(f"+{x}+{y}")
        except Exception:
            self.geometry("+100+100")

        self.after(duration_ms, self.destroy)
