# -*- coding: utf-8 -*-
"""
Fondo animado con efecto Liquid Glass.

Crea un fondo visualmente atractivo con blobs de colores suaves
que se mueven lentamente, simulando un efecto de cristal líquido.
Utiliza PIL/Pillow para generar los frames de animación con
desenfoque gaussiano para bordes suaves.
"""

import tkinter as tk
import math
import time
import logging

try:
    from PIL import Image, ImageDraw, ImageFilter, ImageTk
    PIL_AVAILABLE = True
except ImportError:
    PIL_AVAILABLE = False

from ui.theme import BG_BASE, BLOB_COLORS

logger = logging.getLogger(__name__)


class AnimatedBackground(tk.Canvas):
    """
    Canvas con fondo animado de blobs suaves y coloreados.

    Genera una animación fluida de blobs semitransparentes
    que se mueven en patrones sinusoidales, creando un efecto
    visual de cristal líquido. Utiliza PIL para el renderizado
    de cada frame con desenfoque gaussiano.
    """

    # Intervalo de actualización en milisegundos (~22 FPS)
    UPDATE_INTERVAL = 45

    # Factor de reducción para renderizado eficiente
    SCALE_FACTOR = 6

    def __init__(self, parent, **kwargs):
        """
        Inicializar el fondo animado.

        Args:
            parent: Widget padre de Tkinter.
            **kwargs: Argumentos adicionales para tk.Canvas.
        """
        super().__init__(parent, highlightthickness=0, **kwargs)
        self.configure(bg=BG_BASE)

        # Estado de la animación
        self._running = False
        self._after_id = None
        self._photo_image = None  # Referencia para evitar GC
        self._start_time = time.time()
        self._canvas_width = 1
        self._canvas_height = 1
        self._image_item = None

        # Definición de blobs con parámetros de movimiento
        self.blobs = [
            {
                'base_x': 0.3, 'base_y': 0.3,
                'radius': 0.35,
                'color': BLOB_COLORS[0],
                'freq_x': 0.3, 'freq_y': 0.2,
                'amp': 0.15,
                'phase_x': 0.0, 'phase_y': 0.5
            },
            {
                'base_x': 0.7, 'base_y': 0.6,
                'radius': 0.30,
                'color': BLOB_COLORS[1],
                'freq_x': 0.25, 'freq_y': 0.35,
                'amp': 0.12,
                'phase_x': 1.0, 'phase_y': 0.3
            },
            {
                'base_x': 0.5, 'base_y': 0.8,
                'radius': 0.28,
                'color': BLOB_COLORS[2],
                'freq_x': 0.2, 'freq_y': 0.15,
                'amp': 0.18,
                'phase_x': 2.0, 'phase_y': 1.5
            },
            {
                'base_x': 0.2, 'base_y': 0.5,
                'radius': 0.32,
                'color': BLOB_COLORS[3],
                'freq_x': 0.15, 'freq_y': 0.25,
                'amp': 0.14,
                'phase_x': 0.5, 'phase_y': 2.0
            },
            {
                'base_x': 0.8, 'base_y': 0.2,
                'radius': 0.25,
                'color': BLOB_COLORS[4],
                'freq_x': 0.35, 'freq_y': 0.3,
                'amp': 0.16,
                'phase_x': 1.5, 'phase_y': 0.8
            },
            {
                'base_x': 0.4, 'base_y': 0.1,
                'radius': 0.20,
                'color': BLOB_COLORS[5],
                'freq_x': 0.28, 'freq_y': 0.18,
                'amp': 0.10,
                'phase_x': 0.8, 'phase_y': 1.2
            },
        ]

        # Vincular redimensionamiento
        self.bind('<Configure>', self._on_resize)

    def _on_resize(self, event):
        """
        Manejar el redimensionamiento del canvas.

        Args:
            event: Evento de configuración con nuevo ancho y alto.
        """
        new_w = max(event.width, 1)
        new_h = max(event.height, 1)
        if new_w != self._canvas_width or new_h != self._canvas_height:
            self._canvas_width = new_w
            self._canvas_height = new_h

    def start(self):
        """Iniciar la animación del fondo."""
        if not PIL_AVAILABLE:
            logger.warning("PIL/Pillow no está disponible. Fondo animado desactivado.")
            self._draw_static_background()
            return

        if self._running:
            return

        self._running = True
        self._start_time = time.time()
        logger.info("Animación de fondo iniciada.")
        self._animate()

    def stop(self):
        """Detener la animación del fondo."""
        self._running = False
        if self._after_id is not None:
            try:
                self.after_cancel(self._after_id)
            except Exception:
                pass
            self._after_id = None
        logger.info("Animación de fondo detenida.")

    def _draw_static_background(self):
        """Dibujar un fondo estático si PIL no está disponible."""
        self.configure(bg=BG_BASE)

    def _animate(self):
        """Ejecutar un ciclo de la animación."""
        if not self._running:
            return

        try:
            self._render_frame()
        except tk.TclError:
            # La ventana fue cerrada
            self._running = False
            return
        except Exception as e:
            logger.error(f"Error en la animación: {e}")
            self._running = False
            return

        # Programar el siguiente frame
        try:
            self._after_id = self.after(self.UPDATE_INTERVAL, self._animate)
        except tk.TclError:
            self._running = False

    def _render_frame(self):
        """Renderizar un frame de la animación usando PIL."""
        canvas_w = self._canvas_width
        canvas_h = self._canvas_height

        if canvas_w < 2 or canvas_h < 2:
            return

        # Dimensiones reducidas para rendimiento
        small_w = max(canvas_w // self.SCALE_FACTOR, 2)
        small_h = max(canvas_h // self.SCALE_FACTOR, 2)

        # Parsear el color de fondo base
        bg_r = int(BG_BASE[1:3], 16)
        bg_g = int(BG_BASE[3:5], 16)
        bg_b = int(BG_BASE[5:7], 16)

        # Crear imagen RGBA pequeña
        img = Image.new('RGBA', (small_w, small_h), (bg_r, bg_g, bg_b, 255))

        # Tiempo actual para el cálculo de movimiento
        elapsed = time.time() - self._start_time

        # Dibujar cada blob como una capa semitransparente
        for blob in self.blobs:
            self._draw_blob(img, blob, elapsed, small_w, small_h)

        # Aplicar desenfoque gaussiano para bordes suaves
        img = img.filter(ImageFilter.GaussianBlur(radius=max(small_w // 8, 3)))

        # Convertir a RGB (sin canal alfa para el resultado final)
        img_rgb = Image.new('RGB', (small_w, small_h), (bg_r, bg_g, bg_b))
        img_rgb.paste(img, mask=img.split()[3])

        # Escalar al tamaño completo del canvas
        img_final = img_rgb.resize((canvas_w, canvas_h), Image.BILINEAR)

        # Convertir a PhotoImage de Tkinter
        self._photo_image = ImageTk.PhotoImage(img_final)

        # Actualizar o crear la imagen en el canvas
        if self._image_item is not None:
            try:
                self.itemconfig(self._image_item, image=self._photo_image)
            except tk.TclError:
                self._image_item = self.create_image(
                    0, 0, anchor='nw', image=self._photo_image
                )
        else:
            self._image_item = self.create_image(
                0, 0, anchor='nw', image=self._photo_image
            )

    def _draw_blob(self, img, blob, elapsed, img_w, img_h):
        """
        Dibujar un blob semitransparente sobre la imagen.

        Args:
            img: Imagen PIL RGBA sobre la que dibujar.
            blob: Diccionario con parámetros del blob.
            elapsed: Tiempo transcurrido en segundos.
            img_w: Ancho de la imagen.
            img_h: Alto de la imagen.
        """
        # Calcular posición actual con movimiento sinusoidal
        x = blob['base_x'] + math.sin(elapsed * blob['freq_x'] + blob['phase_x']) * blob['amp']
        y = blob['base_y'] + math.cos(elapsed * blob['freq_y'] + blob['phase_y']) * blob['amp']

        # Convertir a coordenadas de la imagen
        cx = int(x * img_w)
        cy = int(y * img_h)
        radius = int(blob['radius'] * max(img_w, img_h))

        # Crear capa para el blob con transparencia
        blob_layer = Image.new('RGBA', (img_w, img_h), (0, 0, 0, 0))
        draw = ImageDraw.Draw(blob_layer)

        # Dibujar círculo relleno con el color semitransparente
        r, g, b, a = blob['color']
        draw.ellipse(
            [cx - radius, cy - radius, cx + radius, cy + radius],
            fill=(r, g, b, a)
        )

        # Componer sobre la imagen principal
        img.paste(
            Image.alpha_composite(
                Image.new('RGBA', img.size, (0, 0, 0, 0)),
                blob_layer
            ),
            (0, 0),
            blob_layer
        )

    def destroy(self):
        """Destruir el widget deteniendo la animación primero."""
        self.stop()
        self._photo_image = None
        super().destroy()
