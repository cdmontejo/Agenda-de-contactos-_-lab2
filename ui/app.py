# -*- coding: utf-8 -*-
"""
Ventana Principal de la Aplicación con efecto Liquid Glass.

Contiene:
  - Fondo animado fluido con gradientes y blobs de cristal líquido
  - Menú superior tradicional (Requisito de laboratorio)
  - Barra lateral de navegación ejecutiva
  - Contenedor de vistas dinámicas
  - Barra inferior de estado con posición tell()
  - Verificación de integridad automática al arranque
"""

import tkinter as tk
from tkinter import ttk
import logging

from config import APP_NAME, APP_VERSION, APP_SUBTITLE
from services.contact_service import ContactService
from services.export_manager import ExportManager
from services.backup_manager import BackupManager

from ui.theme import (
    apply_theme, BG_BASE, BG_SIDEBAR, BG_GLASS, BG_GLASS_HOVER,
    BORDER_GLASS, TEXT_PRIMARY, TEXT_SECONDARY, TEXT_MUTED,
    ACCENT_PRIMARY, ACCENT_GLOW, COLOR_SUCCESS, COLOR_ERROR,
    FONT_FAMILY, FONT_HEADING_SM, FONT_BODY, FONT_BODY_BOLD,
    FONT_SMALL, FONT_SMALL_BOLD, FONT_TINY
)
from ui.animated_bg import AnimatedBackground
from ui.components import StatusBar, Toast
from ui.dialogs import ErrorDialog, InfoDialog, BackupResultDialog, FileInfoDialog
from ui.contact_form import ContactForm

# Importar vistas
from ui.dashboard_view import DashboardView
from ui.contacts_view import ContactsView
from ui.export_view import ExportView
from ui.tools_view import ToolsView
from ui.help_view import HelpView

logger = logging.getLogger(__name__)


class App(tk.Tk):
    """
    Aplicación principal ContactManager Pro.
    """

    def __init__(self):
        super().__init__()
        self.title(f"{APP_NAME} — {APP_SUBTITLE} (v{APP_VERSION})")
        self.geometry("1280x760")
        self.minsize(1040, 640)
        self.configure(bg=BG_BASE)

        # Centrar en pantalla
        self._center_window(1280, 760)

        # Inicializar Servicios
        self.contact_service = ContactService()
        self.export_manager = ExportManager(self.contact_service)
        self.backup_manager = BackupManager(self.contact_service)

        # Aplicar estilos globales de ttk
        apply_theme(self)

        # Estructura visual
        self._init_layout()
        self._init_menu_bar()
        self._bind_shortcuts()

        # Iniciar fondo animado
        self.anim_bg.start()

        # Verificación de integridad obligatoria al arrancar
        self.after(600, self._check_startup_integrity)

        # Manejo de cierre limpio
        self.protocol("WM_DELETE_WINDOW", self._on_close)

    def _center_window(self, w: int, h: int):
        sw = self.winfo_screenwidth()
        sh = self.winfo_screenheight()
        x = max(0, (sw - w) // 2)
        y = max(0, (sh - h) // 2)
        self.geometry(f"{w}x{h}+{x}+{y}")

    def _init_layout(self):
        # 1. Fondo animado que cubre toda la ventana
        self.anim_bg = AnimatedBackground(self)
        self.anim_bg.place(x=0, y=0, relwidth=1.0, relheight=1.0)

        # 2. Contenedor de interfaz superpuesto (Sidebar + Main + StatusBar)
        self.root_frame = tk.Frame(self, bg='')
        self.root_frame.place(x=0, y=0, relwidth=1.0, relheight=1.0)

        # Barra lateral izquierda
        self.sidebar = tk.Frame(self.root_frame, bg=BG_SIDEBAR, width=240)
        self.sidebar.pack(side='left', fill='y')
        self.sidebar.pack_propagate(False)

        # Borde divisor vertical de cristal
        div = tk.Frame(self.root_frame, bg=BORDER_GLASS, width=1)
        div.pack(side='left', fill='y')

        # Contenedor derecho (Vistas + StatusBar)
        self.right_container = tk.Frame(self.root_frame, bg=BG_BASE)
        self.right_container.pack(side='left', fill='both', expand=True)

        # Barra inferior de estado (tell / pos)
        self.status_bar = StatusBar(self.right_container)
        self.status_bar.pack(side='bottom', fill='x')

        # Contenedor dinámico de vistas
        self.views_container = tk.Frame(self.right_container, bg=BG_BASE)
        self.views_container.pack(side='top', fill='both', expand=True)

        # Construir sidebar y vistas
        self._build_sidebar()
        self._init_views()

    def _build_sidebar(self):
        # Logo y nombre
        logo_box = tk.Frame(self.sidebar, bg=BG_SIDEBAR, pady=24, padx=20)
        logo_box.pack(fill='x')

        lbl_logo = tk.Label(
            logo_box, text="📇 ContactManager", font=FONT_HEADING_SM,
            fg=TEXT_PRIMARY, bg=BG_SIDEBAR, anchor='w'
        )
        lbl_logo.pack(fill='x')

        badge_row = tk.Frame(logo_box, bg=BG_SIDEBAR)
        badge_row.pack(fill='x', pady=(4, 0))

        lbl_badge = tk.Label(
            badge_row, text="ENTERPRISE EDITION", font=FONT_TINY,
            fg=ACCENT_PRIMARY, bg='#231c3d', padx=6, pady=2
        )
        lbl_badge.pack(side='left')

        # Divisor sutil
        tk.Frame(self.sidebar, bg=BORDER_GLASS, height=1).pack(fill='x', padx=16, pady=(10, 16))

        # Items de navegación
        self.nav_items = {}
        items_def = [
            ('dashboard', '🏠  Panel Principal'),
            ('contacts', '👥  Contactos'),
            ('export', '📤  Exportar & Reportes'),
            ('tools', '🔧  Herramientas'),
            ('help', '❓  Ayuda')
        ]

        for key, label in items_def:
            item_frame = tk.Frame(self.sidebar, bg=BG_SIDEBAR, height=44, cursor='hand2')
            item_frame.pack(fill='x', pady=2)
            item_frame.pack_propagate(False)

            indicator = tk.Frame(item_frame, bg=BG_SIDEBAR, width=3)
            indicator.pack(side='left', fill='y')

            lbl = tk.Label(
                item_frame, text=label, font=FONT_BODY,
                fg=TEXT_SECONDARY, bg=BG_SIDEBAR, anchor='w', padx=16
            )
            lbl.pack(side='left', fill='both', expand=True)

            # Bindings para clic y hover
            for widget in (item_frame, lbl):
                widget.bind('<Button-1>', lambda e, k=key: self.navigate_to(k))
                widget.bind('<Enter>', lambda e, f=item_frame, l=lbl, k=key: self._on_nav_hover(f, l, k))
                widget.bind('<Leave>', lambda e, f=item_frame, l=lbl, k=key: self._on_nav_leave(f, l, k))

            self.nav_items[key] = {
                'frame': item_frame,
                'indicator': indicator,
                'label': lbl
            }

        # Espaciador
        spacer = tk.Frame(self.sidebar, bg=BG_SIDEBAR)
        spacer.pack(fill='both', expand=True)

        # Footer de sidebar con estado del índice y versión
        footer_box = tk.Frame(self.sidebar, bg=BG_SIDEBAR, padx=20, pady=16)
        footer_box.pack(fill='x')

        self.lbl_idx_status = tk.Label(
            footer_box, text="Índice: indice.json", font=FONT_TINY,
            fg=TEXT_MUTED, bg=BG_SIDEBAR, anchor='w'
        )
        self.lbl_idx_status.pack(fill='x')

        lbl_ver = tk.Label(
            footer_box, text=f"{APP_NAME} v{APP_VERSION}", font=FONT_TINY,
            fg=TEXT_MUTED, bg=BG_SIDEBAR, anchor='w'
        )
        lbl_ver.pack(fill='x', pady=(2, 0))

    def _init_views(self):
        """Instancia todas las vistas de la aplicación."""
        self.views = {
            'dashboard': DashboardView(self.views_container, self.contact_service, on_navigate=self.navigate_to),
            'contacts': ContactsView(self.views_container, self.contact_service, on_position_update=self._update_position_info),
            'export': ExportView(self.views_container, self.export_manager),
            'tools': ToolsView(self.views_container, self.contact_service, self.backup_manager),
            'help': HelpView(self.views_container)
        }

        self.current_view_key = 'dashboard'
        self.navigate_to('dashboard')

    def navigate_to(self, key: str):
        """Cambia de vista activa."""
        if key == 'contacts_add':
            self.navigate_to('contacts')
            self.views['contacts'].on_add_contact()
            return

        if key not in self.views:
            return

        # Ocultar vista actual
        if hasattr(self, 'current_view_key') and self.current_view_key in self.views:
            self.views[self.current_view_key].pack_forget()

        # Actualizar aspecto del sidebar
        for k, item in self.nav_items.items():
            if k == key:
                item['frame'].configure(bg=BG_GLASS)
                item['label'].configure(fg=TEXT_PRIMARY, bg=BG_GLASS)
                item['indicator'].configure(bg=ACCENT_PRIMARY)
            else:
                item['frame'].configure(bg=BG_SIDEBAR)
                item['label'].configure(fg=TEXT_SECONDARY, bg=BG_SIDEBAR)
                item['indicator'].configure(bg=BG_SIDEBAR)

        # Mostrar nueva vista
        self.current_view_key = key
        self.views[key].pack(fill='both', expand=True)

        # Refrescar vista si soporta refresh
        if hasattr(self.views[key], 'refresh'):
            self.views[key].refresh()

    def _on_nav_hover(self, frame, label, key):
        if key != self.current_view_key:
            frame.configure(bg=BG_GLASS_HOVER)
            label.configure(bg=BG_GLASS_HOVER)

    def _on_nav_leave(self, frame, label, key):
        if key != self.current_view_key:
            frame.configure(bg=BG_SIDEBAR)
            label.configure(bg=BG_SIDEBAR)

    def _init_menu_bar(self):
        """
        Menú superior tradicional solicitado en las instrucciones del laboratorio:
          - Contactos (agregar, buscar por ID, modificar)
          - Exportar (exportar a JSON, generar reporte PDF)
          - Herramientas (verificar integridad, crear respaldo ZIP, información del archivo)
          - Ayuda (simulado)
        """
        menubar = tk.Menu(self)

        # Menú Contactos
        menu_contactos = tk.Menu(menubar, tearoff=0)
        menu_contactos.add_command(label="➕ Agregar Contacto", command=lambda: self.navigate_to('contacts_add'), accelerator="Ctrl+N")
        menu_contactos.add_command(label="🔍 Buscar por ID", command=lambda: (self.navigate_to('contacts'), self.views['contacts'].on_search_by_id()), accelerator="Ctrl+F")
        menu_contactos.add_command(label="✏ Modificar Contacto Seleccionado", command=lambda: (self.navigate_to('contacts'), self.views['contacts'].on_edit_selected()))
        menu_contactos.add_separator()
        menu_contactos.add_command(label="Salir", command=self._on_close)
        menubar.add_cascade(label="Contactos", menu=menu_contactos)

        # Menú Exportar
        menu_export = tk.Menu(menubar, tearoff=0)
        menu_export.add_command(label="📄 Exportar a JSON", command=lambda: self.views['export'].on_export_json(), accelerator="Ctrl+E")
        menu_export.add_command(label="📊 Generar Reporte PDF", command=lambda: self.views['export'].on_export_pdf())
        menu_export.add_command(label="📋 Exportar a CSV", command=lambda: self.views['export'].on_export_csv())
        menubar.add_cascade(label="Exportar", menu=menu_export)

        # Menú Herramientas
        menu_tools = tk.Menu(menubar, tearoff=0)
        menu_tools.add_command(label="🛡 Verificar Integridad (SHA-256)", command=lambda: self.views['tools'].on_verify_integrity())
        menu_tools.add_command(label="📦 Crear Respaldo ZIP", command=lambda: self.views['tools'].on_create_backup(), accelerator="Ctrl+B")
        menu_tools.add_command(label="ℹ Información Técnica del Archivo", command=lambda: self.views['tools'].on_show_file_info())
        menu_tools.add_separator()
        menu_tools.add_command(label="⚙ Reconstruir Índice Primario", command=lambda: self.views['tools'].on_rebuild_index())
        menubar.add_cascade(label="Herramientas", menu=menu_tools)

        # Menú Ayuda (Simulado)
        menu_help = tk.Menu(menubar, tearoff=0)
        menu_help.add_command(label="Guía Rápida & Acceso Aleatorio", command=lambda: self.navigate_to('help'))
        menu_help.add_command(label="Acerca de ContactManager Pro", command=lambda: InfoDialog(
            self, "Acerca de",
            f"{APP_NAME} v{APP_VERSION}\n\n"
            "Sistema de Gestión de Contactos con Acceso Aleatorio.\n"
            "Laboratorio No. 2 - Estructuras de Datos Avanzadas.\n"
            "Facultad de Ingeniería - Octubre 2026."
        ))
        menubar.add_cascade(label="Ayuda", menu=menu_help)

        self.config(menu=menubar)

    def _bind_shortcuts(self):
        self.bind('<Control-n>', lambda e: self.navigate_to('contacts_add'))
        self.bind('<Control-N>', lambda e: self.navigate_to('contacts_add'))
        self.bind('<Control-f>', lambda e: (self.navigate_to('contacts'), self.views['contacts'].on_search_by_id()))
        self.bind('<Control-F>', lambda e: (self.navigate_to('contacts'), self.views['contacts'].on_search_by_id()))
        self.bind('<Control-e>', lambda e: self.views['export'].on_export_json())
        self.bind('<Control-E>', lambda e: self.views['export'].on_export_json())
        self.bind('<Control-b>', lambda e: self.views['tools'].on_create_backup())
        self.bind('<Control-B>', lambda e: self.views['tools'].on_create_backup())
        self.bind('<F5>', lambda e: self._refresh_all())

    def _refresh_all(self):
        for v in self.views.values():
            if hasattr(v, 'refresh'):
                v.refresh()
        Toast(self, "Datos y estadísticas actualizados", toast_type='info')

    def _update_position_info(self, position_bytes: int, record_num: int = None):
        self.status_bar.set_position_info(position_bytes, record_num)

    def _check_startup_integrity(self):
        """
        Requisito explícito:
        Al iniciar la aplicación, se recalcula el hash SHA-256 y se compara;
        si no coincide, se avisa al usuario que el archivo fue modificado fuera
        de la aplicación.
        """
        ok, msg = self.contact_service.verify_integrity()
        if not ok:
            ErrorDialog(
                self, "Alerta de Integridad Detectada al Inicio",
                f"⚠ ADVERTENCIA DE SEGURIDAD:\n\n{msg}\n\n"
                "El archivo 'contactos.dat' fue modificado fuera de la aplicación "
                "o presenta discrepancia criptográfica en su hash SHA-256.\n"
                "Puede verificar el estado en el menú Herramientas -> Verificar Integridad."
            )
            self.status_bar.set_status("Discrepancia en hash SHA-256 detectada", is_error=True)
        else:
            self.status_bar.set_status("Integridad verificada (SHA-256 coincide)")

    def _on_close(self):
        """Cierre ordenado y detención del bucle de animación."""
        self.anim_bg.stop()
        self.destroy()
