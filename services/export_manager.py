"""
Gestor de exportaciones para la Agenda de Contactos.

Permite exportar los contactos activos a múltiples formatos:
  - JSON: formato estructurado legible
  - CSV:  compatible con hojas de cálculo (con BOM UTF-8)
  - PDF:  reporte profesional con tabla formateada

Cada exportación genera un archivo con marca de tiempo para
evitar sobreescrituras accidentales.
"""

import os
import json
import csv
import logging
from datetime import datetime

import sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from config import EXPORTS_DIR, APP_NAME, APP_VERSION

logger = logging.getLogger(__name__)


class ExportManager:
    """
    Gestiona la exportación de contactos a diferentes formatos.
    """

    def __init__(self, contact_service):
        """
        Inicializa el gestor de exportaciones.

        Args:
            contact_service: Instancia de ContactService para
                             obtener los contactos.
        """
        self.contact_service = contact_service

    def _generate_filepath(self, extension: str) -> str:
        """
        Genera una ruta de archivo con marca de tiempo.

        Args:
            extension: Extensión del archivo (sin punto).

        Returns:
            Ruta completa al archivo de exportación.
        """
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        filename = f"contactos_{timestamp}.{extension}"
        return os.path.join(EXPORTS_DIR, filename)

    def export_json(self, filepath: str = None) -> tuple[bool, str, str]:
        """
        Exporta los contactos activos a un archivo JSON.

        Args:
            filepath: Ruta de destino. Si es ``None``, se genera
                      automáticamente en el directorio de exportaciones.

        Returns:
            Tupla (éxito, mensaje, ruta_archivo).
        """
        if filepath is None:
            filepath = self._generate_filepath('json')

        try:
            contacts = self.contact_service.get_all_contacts(
                include_deleted=False
            )

            export_data = {
                'metadata': {
                    'application': APP_NAME,
                    'version': APP_VERSION,
                    'exported_at': datetime.now().isoformat(),
                    'total_contacts': len(contacts),
                },
                'contacts': contacts,
            }

            os.makedirs(os.path.dirname(filepath), exist_ok=True)

            with open(filepath, 'w', encoding='utf-8') as f:
                json.dump(
                    export_data, f,
                    ensure_ascii=False,
                    indent=2,
                    sort_keys=False
                )

            logger.info(
                "Exportación JSON exitosa: %d contactos -> %s",
                len(contacts), filepath
            )

            return (
                True,
                f"Se exportaron {len(contacts)} contactos a JSON",
                filepath
            )

        except (OSError, PermissionError) as exc:
            logger.error("Error en exportación JSON: %s", exc)
            return (False, f"Error al exportar a JSON: {exc}", "")
        except Exception as exc:
            logger.error("Error inesperado en exportación JSON: %s", exc)
            return (False, f"Error inesperado: {exc}", "")

    def export_pdf(self, filepath: str = None) -> tuple[bool, str, str]:
        """
        Exporta los contactos activos a un reporte PDF profesional.

        Genera un documento con título, subtítulo, fecha, tabla de
        contactos y pie de página con numeración.

        Args:
            filepath: Ruta de destino. Si es ``None``, se genera
                      automáticamente.

        Returns:
            Tupla (éxito, mensaje, ruta_archivo).
        """
        if filepath is None:
            filepath = self._generate_filepath('pdf')

        try:
            from fpdf import FPDF
        except ImportError:
            logger.error("fpdf2 no está instalado")
            return (
                False,
                "Error: la librería fpdf2 no está instalada. "
                "Ejecute: pip install fpdf2",
                ""
            )

        try:
            contacts = self.contact_service.get_all_contacts(
                include_deleted=False
            )

            os.makedirs(os.path.dirname(filepath), exist_ok=True)

            # Crear PDF
            pdf = FPDF(orientation='L', unit='mm', format='A4')
            pdf.set_auto_page_break(auto=True, margin=20)

            # ── Encabezado y primera página ──
            pdf.add_page()

            # Título
            pdf.set_font('Helvetica', 'B', 20)
            pdf.cell(
                0, 12,
                self._safe_latin1("Reporte de Contactos"),
                ln=True, align='C'
            )

            # Subtítulo
            pdf.set_font('Helvetica', '', 12)
            pdf.cell(
                0, 8,
                self._safe_latin1(APP_NAME),
                ln=True, align='C'
            )

            # Fecha de generación
            pdf.set_font('Helvetica', 'I', 10)
            fecha = datetime.now().strftime('%d/%m/%Y %H:%M:%S')
            pdf.cell(
                0, 8,
                self._safe_latin1(f"Generado el: {fecha}"),
                ln=True, align='C'
            )

            # Línea separadora
            pdf.ln(4)
            pdf.set_draw_color(0, 102, 204)
            pdf.set_line_width(0.5)
            pdf.line(10, pdf.get_y(), 287, pdf.get_y())
            pdf.ln(6)

            # Total de contactos
            pdf.set_font('Helvetica', '', 10)
            pdf.cell(
                0, 6,
                self._safe_latin1(
                    f"Total de contactos activos: {len(contacts)}"
                ),
                ln=True
            )
            pdf.ln(4)

            # ── Tabla de contactos ──
            # Anchos de columna (paisaje A4 = ~277mm útiles)
            col_widths = {
                'id': 20,
                'nombre': 65,
                'telefono': 45,
                'correo': 85,
                'ciudad': 52,
            }

            # Encabezados de tabla
            pdf.set_font('Helvetica', 'B', 10)
            pdf.set_fill_color(0, 102, 204)
            pdf.set_text_color(255, 255, 255)

            headers = [
                ('ID', col_widths['id']),
                ('Nombre', col_widths['nombre']),
                (self._safe_latin1('Teléfono'), col_widths['telefono']),
                ('Correo', col_widths['correo']),
                ('Ciudad', col_widths['ciudad']),
            ]

            for header_text, width in headers:
                pdf.cell(width, 8, header_text, border=1, fill=True, align='C')
            pdf.ln()

            # Filas de datos
            pdf.set_font('Helvetica', '', 9)
            pdf.set_text_color(0, 0, 0)

            for i, contact in enumerate(contacts):
                # Alternar color de fondo
                if i % 2 == 0:
                    pdf.set_fill_color(245, 245, 245)
                else:
                    pdf.set_fill_color(255, 255, 255)

                pdf.cell(
                    col_widths['id'], 7,
                    self._safe_latin1(str(contact.get('id', ''))),
                    border=1, fill=True, align='C'
                )
                pdf.cell(
                    col_widths['nombre'], 7,
                    self._safe_latin1(
                        self._truncate_text(contact.get('nombre', ''), 35)
                    ),
                    border=1, fill=True
                )
                pdf.cell(
                    col_widths['telefono'], 7,
                    self._safe_latin1(contact.get('telefono', '')),
                    border=1, fill=True, align='C'
                )
                pdf.cell(
                    col_widths['correo'], 7,
                    self._safe_latin1(
                        self._truncate_text(contact.get('correo', ''), 45)
                    ),
                    border=1, fill=True
                )
                pdf.cell(
                    col_widths['ciudad'], 7,
                    self._safe_latin1(
                        self._truncate_text(contact.get('ciudad', ''), 28)
                    ),
                    border=1, fill=True
                )
                pdf.ln()

            # ── Pie de página ──
            pdf.ln(10)
            pdf.set_font('Helvetica', 'I', 8)
            pdf.set_text_color(128, 128, 128)
            pdf.cell(
                0, 5,
                self._safe_latin1(
                    f"{APP_NAME} v{APP_VERSION} | "
                    f"Página {pdf.page_no()}"
                ),
                align='C'
            )

            # Guardar PDF
            pdf.output(filepath)

            logger.info(
                "Exportación PDF exitosa: %d contactos -> %s",
                len(contacts), filepath
            )

            return (
                True,
                f"Se exportaron {len(contacts)} contactos a PDF",
                filepath
            )

        except Exception as exc:
            logger.error("Error en exportación PDF: %s", exc)
            return (False, f"Error al exportar a PDF: {exc}", "")

    def export_csv(self, filepath: str = None) -> tuple[bool, str, str]:
        """
        Exporta los contactos activos a un archivo CSV.

        Incluye BOM UTF-8 al inicio del archivo para compatibilidad
        con Microsoft Excel.

        Args:
            filepath: Ruta de destino. Si es ``None``, se genera
                      automáticamente.

        Returns:
            Tupla (éxito, mensaje, ruta_archivo).
        """
        if filepath is None:
            filepath = self._generate_filepath('csv')

        try:
            contacts = self.contact_service.get_all_contacts(
                include_deleted=False
            )

            os.makedirs(os.path.dirname(filepath), exist_ok=True)

            with open(filepath, 'w', encoding='utf-8-sig', newline='') as f:
                writer = csv.writer(f)

                # Encabezados
                writer.writerow([
                    'ID', 'Nombre', 'Teléfono', 'Correo', 'Ciudad'
                ])

                # Datos
                for contact in contacts:
                    writer.writerow([
                        contact.get('id', ''),
                        contact.get('nombre', ''),
                        contact.get('telefono', ''),
                        contact.get('correo', ''),
                        contact.get('ciudad', ''),
                    ])

            logger.info(
                "Exportación CSV exitosa: %d contactos -> %s",
                len(contacts), filepath
            )

            return (
                True,
                f"Se exportaron {len(contacts)} contactos a CSV",
                filepath
            )

        except (OSError, PermissionError) as exc:
            logger.error("Error en exportación CSV: %s", exc)
            return (False, f"Error al exportar a CSV: {exc}", "")
        except Exception as exc:
            logger.error("Error inesperado en exportación CSV: %s", exc)
            return (False, f"Error inesperado: {exc}", "")

    @staticmethod
    def _safe_latin1(text: str) -> str:
        """
        Convierte texto a latin-1 seguro para FPDF con fuentes estándar.

        Reemplaza caracteres que no se pueden representar en latin-1
        con su equivalente más cercano o con '?'.

        Args:
            text: Texto a convertir.

        Returns:
            Texto seguro para latin-1.
        """
        try:
            text.encode('latin-1')
            return text
        except (UnicodeEncodeError, UnicodeDecodeError):
            # Reemplazo carácter a carácter
            result = []
            for char in text:
                try:
                    char.encode('latin-1')
                    result.append(char)
                except UnicodeEncodeError:
                    result.append('?')
            return ''.join(result)

    @staticmethod
    def _truncate_text(text: str, max_length: int) -> str:
        """
        Trunca texto añadiendo '...' si excede el límite.

        Args:
            text:       Texto original.
            max_length: Longitud máxima.

        Returns:
            Texto truncado o el original si no excede.
        """
        if len(text) <= max_length:
            return text
        return text[:max_length - 3] + '...'
