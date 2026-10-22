# -*- coding: utf-8 -*-
"""
Configuración del tema visual Liquid Glass.

Define todas las constantes de colores, tipografía, espaciado y
configura los estilos ttk para toda la aplicación.
"""

import tkinter as tk
from tkinter import ttk

# =============================================================================
# PALETA DE COLORES - Tema Oscuro Liquid Glass
# =============================================================================

# Fondos principales
BG_BASE = '#0a0a1a'            # Fondo base muy oscuro (navy profundo)
BG_GLASS = '#16162a'           # Fondo de paneles de cristal
BG_GLASS_HOVER = '#1e1e38'     # Fondo de cristal al pasar el ratón
BG_SIDEBAR = '#0e0e22'         # Fondo del sidebar (cristal más oscuro)
BG_CARD = '#1a1a32'            # Fondo de tarjetas (ligeramente más claro)
BG_INPUT = '#12122a'           # Fondo de campos de entrada
BG_TABLE_HEADER = '#0e0e22'    # Fondo del encabezado de tabla

# Bordes
BORDER_GLASS = '#2a2a4a'       # Borde sutil de paneles
BORDER_INPUT = '#2a2a4a'       # Borde de campos de entrada
BORDER_FOCUS = '#8b5cf6'       # Borde de foco (púrpura)

# Texto
TEXT_PRIMARY = '#f0f0f8'        # Texto principal
TEXT_SECONDARY = '#8888a8'      # Texto secundario
TEXT_MUTED = '#5a5a78'          # Texto atenuado

# Acentos
ACCENT_PRIMARY = '#8b5cf6'     # Púrpura principal
ACCENT_HOVER = '#7c3aed'       # Púrpura al pasar el ratón
ACCENT_GLOW = '#a78bfa'        # Brillo púrpura

# Estados semánticos
COLOR_SUCCESS = '#10b981'      # Verde éxito
COLOR_WARNING = '#f59e0b'      # Ámbar advertencia
COLOR_ERROR = '#ef4444'        # Rojo error
COLOR_INFO = '#3b82f6'         # Azul información

# Botones
BTN_PRIMARY_BG = '#8b5cf6'     # Fondo botón primario
BTN_PRIMARY_HOVER = '#7c3aed'  # Hover botón primario
BTN_SECONDARY_BG = '#1e1e38'   # Fondo botón secundario
BTN_SECONDARY_HOVER = '#2a2a4a'  # Hover botón secundario
BTN_SUCCESS_BG = '#059669'     # Fondo botón éxito
BTN_SUCCESS_HOVER = '#047857'  # Hover botón éxito
BTN_DANGER_BG = '#dc2626'      # Fondo botón peligro
BTN_DANGER_HOVER = '#b91c1c'   # Hover botón peligro

# Scrollbar
SCROLLBAR_COLOR = '#2a2a4a'    # Color del scrollbar

# Tabla
TABLE_ROW_HOVER = '#1e1e38'    # Fila al pasar el ratón
TABLE_ROW_ALT = '#141428'      # Fila alternada

# Colores de blobs para fondo animado (RGBA para PIL)
BLOB_COLORS = [
    (139, 92, 246, 120),   # Púrpura
    (59, 130, 246, 100),   # Azul
    (236, 72, 153, 90),    # Rosa
    (20, 184, 166, 80),    # Teal
    (99, 102, 241, 100),   # Índigo
    (168, 85, 247, 70),    # Púrpura claro
]

# =============================================================================
# TIPOGRAFÍA
# =============================================================================

FONT_FAMILY = 'Segoe UI'
FONT_FAMILY_MONO = 'Consolas'
FONT_FALLBACK = ('Helvetica', 'Arial')

FONT_HEADING_LG = (FONT_FAMILY, 24, 'bold')
FONT_HEADING_MD = (FONT_FAMILY, 18)
FONT_HEADING_SM = (FONT_FAMILY, 14)
FONT_BODY = (FONT_FAMILY, 13)
FONT_BODY_BOLD = (FONT_FAMILY, 13, 'bold')
FONT_SMALL = (FONT_FAMILY, 11)
FONT_SMALL_BOLD = (FONT_FAMILY, 11, 'bold')
FONT_TINY = (FONT_FAMILY, 10)
FONT_MONO = (FONT_FAMILY_MONO, 12)
FONT_MONO_SMALL = (FONT_FAMILY_MONO, 10)

# =============================================================================
# ESPACIADO
# =============================================================================

PAD_PAGE = 24          # Padding de página
PAD_CARD = 20          # Padding de tarjeta
PAD_ELEMENT = 12       # Espacio entre elementos
PAD_SECTION = 24       # Espacio entre secciones
PAD_SMALL = 6          # Espacio pequeño
PAD_TINY = 4           # Espacio diminuto

# =============================================================================
# DIMENSIONES
# =============================================================================

SIDEBAR_WIDTH = 240    # Ancho del sidebar
STATUSBAR_HEIGHT = 32  # Alto de la barra de estado
BUTTON_HEIGHT = 38     # Alto de botones
ENTRY_HEIGHT = 36      # Alto de campos de entrada
CARD_RADIUS = 8        # Radio de esquinas de tarjetas
BUTTON_RADIUS = 6      # Radio de esquinas de botones
NAV_ITEM_HEIGHT = 42   # Alto de items de navegación
NAV_INDICATOR_WIDTH = 3  # Ancho del indicador de navegación activa


def apply_theme(root):
    """
    Aplica el tema Liquid Glass a toda la aplicación.

    Configura los estilos ttk para todos los widgets utilizados
    en la aplicación, creando una apariencia oscura y elegante
    inspirada en el diseño de cristal líquido.

    Args:
        root: La ventana raíz de Tkinter.
    """
    style = ttk.Style(root)

    # Intentar usar el tema 'clam' como base (mejor soporte de personalización)
    try:
        style.theme_use('clam')
    except tk.TclError:
        pass

    # -------------------------------------------------------------------------
    # TFrame
    # -------------------------------------------------------------------------
    style.configure('TFrame',
                    background=BG_BASE)

    # Glass.TFrame - Panel con efecto cristal
    style.configure('Glass.TFrame',
                    background=BG_GLASS,
                    borderwidth=1,
                    relief='flat')

    # Sidebar.TFrame - Panel del sidebar
    style.configure('Sidebar.TFrame',
                    background=BG_SIDEBAR)

    # Card.TFrame - Tarjeta
    style.configure('Card.TFrame',
                    background=BG_CARD)

    # -------------------------------------------------------------------------
    # TLabel
    # -------------------------------------------------------------------------
    style.configure('TLabel',
                    background=BG_BASE,
                    foreground=TEXT_PRIMARY,
                    font=FONT_BODY)

    # Glass.TLabel - Label sobre panel cristal
    style.configure('Glass.TLabel',
                    background=BG_GLASS,
                    foreground=TEXT_PRIMARY,
                    font=FONT_BODY)

    # Heading.TLabel
    style.configure('Heading.TLabel',
                    background=BG_BASE,
                    foreground=TEXT_PRIMARY,
                    font=FONT_HEADING_LG)

    # SubHeading.TLabel
    style.configure('SubHeading.TLabel',
                    background=BG_BASE,
                    foreground=TEXT_SECONDARY,
                    font=FONT_HEADING_SM)

    # Secondary.TLabel
    style.configure('Secondary.TLabel',
                    background=BG_BASE,
                    foreground=TEXT_SECONDARY,
                    font=FONT_BODY)

    # Muted.TLabel
    style.configure('Muted.TLabel',
                    background=BG_BASE,
                    foreground=TEXT_MUTED,
                    font=FONT_SMALL)

    # Card.TLabel - Label sobre tarjeta
    style.configure('Card.TLabel',
                    background=BG_CARD,
                    foreground=TEXT_PRIMARY,
                    font=FONT_BODY)

    # Sidebar.TLabel
    style.configure('Sidebar.TLabel',
                    background=BG_SIDEBAR,
                    foreground=TEXT_PRIMARY,
                    font=FONT_BODY)

    # -------------------------------------------------------------------------
    # TButton
    # -------------------------------------------------------------------------
    style.configure('TButton',
                    background=BTN_SECONDARY_BG,
                    foreground=TEXT_PRIMARY,
                    font=FONT_BODY,
                    borderwidth=0,
                    focuscolor='none',
                    padding=(16, 8))

    style.map('TButton',
              background=[('active', BTN_SECONDARY_HOVER),
                          ('pressed', BTN_SECONDARY_HOVER)])

    # Accent.TButton - Botón primario púrpura
    style.configure('Accent.TButton',
                    background=BTN_PRIMARY_BG,
                    foreground='#ffffff',
                    font=FONT_BODY_BOLD,
                    borderwidth=0,
                    focuscolor='none',
                    padding=(16, 8))

    style.map('Accent.TButton',
              background=[('active', BTN_PRIMARY_HOVER),
                          ('pressed', BTN_PRIMARY_HOVER)])

    # Secondary.TButton
    style.configure('Secondary.TButton',
                    background=BTN_SECONDARY_BG,
                    foreground=TEXT_PRIMARY,
                    font=FONT_BODY,
                    borderwidth=1,
                    focuscolor='none',
                    padding=(16, 8))

    style.map('Secondary.TButton',
              background=[('active', BTN_SECONDARY_HOVER),
                          ('pressed', BTN_SECONDARY_HOVER)])

    # Success.TButton
    style.configure('Success.TButton',
                    background=BTN_SUCCESS_BG,
                    foreground='#ffffff',
                    font=FONT_BODY_BOLD,
                    borderwidth=0,
                    focuscolor='none',
                    padding=(16, 8))

    style.map('Success.TButton',
              background=[('active', BTN_SUCCESS_HOVER),
                          ('pressed', BTN_SUCCESS_HOVER)])

    # Danger.TButton
    style.configure('Danger.TButton',
                    background=BTN_DANGER_BG,
                    foreground='#ffffff',
                    font=FONT_BODY_BOLD,
                    borderwidth=0,
                    focuscolor='none',
                    padding=(16, 8))

    style.map('Danger.TButton',
              background=[('active', BTN_DANGER_HOVER),
                          ('pressed', BTN_DANGER_HOVER)])

    # -------------------------------------------------------------------------
    # TEntry
    # -------------------------------------------------------------------------
    style.configure('TEntry',
                    fieldbackground=BG_INPUT,
                    foreground=TEXT_PRIMARY,
                    insertcolor=TEXT_PRIMARY,
                    borderwidth=1,
                    font=FONT_BODY,
                    padding=(8, 6))

    style.map('TEntry',
              bordercolor=[('focus', BORDER_FOCUS),
                           ('!focus', BORDER_INPUT)],
              lightcolor=[('focus', BORDER_FOCUS)],
              darkcolor=[('focus', BORDER_FOCUS)])

    # -------------------------------------------------------------------------
    # Treeview
    # -------------------------------------------------------------------------
    style.configure('Treeview',
                    background=BG_GLASS,
                    foreground=TEXT_PRIMARY,
                    fieldbackground=BG_GLASS,
                    borderwidth=0,
                    font=FONT_BODY,
                    rowheight=36)

    style.configure('Treeview.Heading',
                    background=BG_TABLE_HEADER,
                    foreground=TEXT_SECONDARY,
                    font=FONT_SMALL_BOLD,
                    borderwidth=0,
                    relief='flat',
                    padding=(8, 6))

    style.map('Treeview',
              background=[('selected', ACCENT_PRIMARY)],
              foreground=[('selected', '#ffffff')])

    style.map('Treeview.Heading',
              background=[('active', BG_GLASS_HOVER)])

    # -------------------------------------------------------------------------
    # Vertical.TScrollbar
    # -------------------------------------------------------------------------
    style.configure('Vertical.TScrollbar',
                    background=BG_BASE,
                    troughcolor=BG_BASE,
                    borderwidth=0,
                    arrowsize=0,
                    width=8)

    style.map('Vertical.TScrollbar',
              background=[('active', SCROLLBAR_COLOR),
                          ('!active', BORDER_GLASS)])

    # -------------------------------------------------------------------------
    # TNotebook
    # -------------------------------------------------------------------------
    style.configure('TNotebook',
                    background=BG_BASE,
                    borderwidth=0)

    style.configure('TNotebook.Tab',
                    background=BG_GLASS,
                    foreground=TEXT_SECONDARY,
                    font=FONT_BODY,
                    padding=(16, 8),
                    borderwidth=0)

    style.map('TNotebook.Tab',
              background=[('selected', ACCENT_PRIMARY)],
              foreground=[('selected', '#ffffff')])

    # -------------------------------------------------------------------------
    # TCombobox
    # -------------------------------------------------------------------------
    style.configure('TCombobox',
                    fieldbackground=BG_INPUT,
                    background=BG_INPUT,
                    foreground=TEXT_PRIMARY,
                    arrowcolor=TEXT_SECONDARY,
                    borderwidth=1,
                    font=FONT_BODY,
                    padding=(8, 6))

    style.map('TCombobox',
              fieldbackground=[('readonly', BG_INPUT)],
              foreground=[('readonly', TEXT_PRIMARY)],
              bordercolor=[('focus', BORDER_FOCUS),
                           ('!focus', BORDER_INPUT)])

    # Configurar el fondo del dropdown del Combobox
    try:
        root.option_add('*TCombobox*Listbox.background', BG_INPUT)
        root.option_add('*TCombobox*Listbox.foreground', TEXT_PRIMARY)
        root.option_add('*TCombobox*Listbox.selectBackground', ACCENT_PRIMARY)
        root.option_add('*TCombobox*Listbox.selectForeground', '#ffffff')
        root.option_add('*TCombobox*Listbox.font', FONT_BODY)
    except Exception:
        pass

    # -------------------------------------------------------------------------
    # TSeparator
    # -------------------------------------------------------------------------
    style.configure('TSeparator',
                    background=BORDER_GLASS)

    # -------------------------------------------------------------------------
    # TProgressbar
    # -------------------------------------------------------------------------
    style.configure('TProgressbar',
                    background=ACCENT_PRIMARY,
                    troughcolor=BG_INPUT,
                    borderwidth=0)

    # Configurar el fondo de la ventana raíz
    root.configure(bg=BG_BASE)
