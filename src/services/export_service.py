"""
Servicio de exportaciones y generación de reportes ejecutivos para ContactHub Enterprise.
Permite exportar a JSON estructurado, CSV con BOM para Microsoft Excel y PDF profesional con fpdf2.
"""

import os
import csv
import json
import logging
from datetime import datetime
from pathlib import Path
from typing import Tuple, List, Dict, Any, Optional

from fpdf import FPDF

import sys
sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent))
from config import EXPORTS_DIR, APP_NAME, APP_VERSION, APP_ORGANIZATION

logger = logging.getLogger("services.export_service")


def _safe_str(text: Any) -> str:
    """Reemplaza caracteres no soportados por fuentes estándar de PDF (latin-1)."""
    s = str(text or "")
    s = s.replace("—", "-").replace("–", "-").replace("“", '"').replace("”", '"')
    return s.encode("latin-1", "replace").decode("latin-1")


class ExecutivePDFReport(FPDF):
    """Generador de reportes PDF con diseño corporativo empresarial."""

    def __init__(self, title_text: str = "Reporte Ejecutivo de Contactos"):
        super().__init__(orientation="P", unit="mm", format="A4")
        self.set_auto_page_break(auto=True, margin=18)
        self.title_text = _safe_str(title_text)
        self.generation_date = datetime.now().strftime("%d/%m/%Y %H:%M:%S")

    def header(self):
        # Fondo sutil de barra superior
        self.set_fill_color(16, 25, 42)  # #10192A
        self.rect(0, 0, 210, 18, "F")

        # Texto de cabecera
        self.set_xy(12, 4)
        self.set_font("Helvetica", "B", 10)
        self.set_text_color(31, 168, 255)  # #1FA8FF
        self.cell(0, 5, _safe_str(f"{APP_NAME} - {APP_ORGANIZATION}"), align="L")

        self.set_xy(12, 9)
        self.set_font("Helvetica", "", 8)
        self.set_text_color(141, 164, 191)  # #8DA4BF
        self.cell(0, 5, f"Generado: {self.generation_date}", align="L")

        self.ln(12)

    def footer(self):
        self.set_y(-14)
        self.set_draw_color(226, 232, 240)
        self.line(12, self.get_y(), 198, self.get_y())

        self.set_font("Helvetica", "I", 8)
        self.set_text_color(100, 116, 139)
        self.cell(0, 8, _safe_str(f"Pagina {self.page_no()}/{{nb}} - Acceso Aleatorio O(1) con Registros Fijos de 256B"), align="C")


class ExportService:
    """
    Controlador de exportaciones a múltiples formatos empresariales.
    """

    def __init__(self, contact_service=None, exports_dir: Path | str = EXPORTS_DIR):
        self.contact_service = contact_service
        self.exports_dir = Path(exports_dir)
        self.exports_dir.mkdir(parents=True, exist_ok=True)

    def _generate_path(self, extension: str, prefix: str = "contactos") -> Path:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"{prefix}_{timestamp}.{extension}"
        return self.exports_dir / filename

    def export_json(self, filepath: Optional[Path | str] = None) -> Tuple[bool, str, str]:
        """Exporta los contactos activos en JSON legible y enriquecido con metadatos."""
        if not self.contact_service:
            return False, "Servicio de contactos no disponible.", ""

        out_path = Path(filepath) if filepath else self._generate_path("json")
        try:
            contacts = self.contact_service.get_all_contacts(include_deleted=False)
            stats = self.contact_service.get_statistics()
            current_hash = self.contact_service.integrity_manager.get_stored_hash()

            payload = {
                "metadata": {
                    "application": APP_NAME,
                    "version": APP_VERSION,
                    "generated_at": datetime.now().isoformat(),
                    "total_active_records": len(contacts),
                    "source_sha256": current_hash,
                    "record_size_bytes": 256
                },
                "contacts": contacts
            }

            with open(out_path, "w", encoding="utf-8") as f:
                json.dump(payload, f, indent=2, ensure_ascii=False)

            msg = f"Exportación JSON completada: {out_path.name} ({len(contacts)} contactos)."
            logger.info(msg)
            return True, msg, str(out_path)

        except Exception as exc:
            logger.error("Error al exportar JSON: %s", exc)
            return False, f"Fallo al exportar JSON: {exc}", ""

    def export_csv(self, filepath: Optional[Path | str] = None, delimiter: str = ",") -> Tuple[bool, str, str]:
        """Exporta los contactos a formato CSV con BOM UTF-8 (compatible con Excel)."""
        if not self.contact_service:
            return False, "Servicio de contactos no disponible.", ""

        out_path = Path(filepath) if filepath else self._generate_path("csv")
        try:
            contacts = self.contact_service.get_all_contacts(include_deleted=False)

            with open(out_path, "w", encoding="utf-8-sig", newline="") as f:
                writer = csv.writer(f, delimiter=delimiter)
                writer.writerow(["ID", "Nombre Completo", "Teléfono", "Correo Electrónico", "Ciudad", "Estado", "Offset (Bytes)", "Registro #"])

                for c in contacts:
                    writer.writerow([
                        c.get("id"),
                        c.get("nombre"),
                        c.get("telefono"),
                        c.get("correo"),
                        c.get("ciudad"),
                        c.get("estado"),
                        c.get("byte_offset"),
                        c.get("record_num")
                    ])

            msg = f"Exportación CSV completada: {out_path.name} ({len(contacts)} filas)."
            logger.info(msg)
            return True, msg, str(out_path)

        except Exception as exc:
            logger.error("Error al exportar CSV: %s", exc)
            return False, f"Fallo al exportar CSV: {exc}", ""

    def export_pdf(self, filepath: Optional[Path | str] = None) -> Tuple[bool, str, str]:
        """Genera un reporte PDF corporativo de alta calidad con fpdf2."""
        if not self.contact_service:
            return False, "Servicio de contactos no disponible.", ""

        out_path = Path(filepath) if filepath else self._generate_path("pdf")
        try:
            contacts = self.contact_service.get_all_contacts(include_deleted=False)
            stats = self.contact_service.get_statistics()
            current_hash = self.contact_service.integrity_manager.get_stored_hash()

            pdf = ExecutivePDFReport(title_text="Directorio Empresarial de Contactos")
            pdf.alias_nb_pages()
            pdf.add_page()

            # Título principal del documento
            pdf.set_font("Helvetica", "B", 18)
            pdf.set_text_color(15, 23, 42)
            pdf.cell(0, 10, "Directorio Ejecutivo de Contactos", ln=True, align="L")

            pdf.set_font("Helvetica", "", 10)
            pdf.set_text_color(100, 116, 139)
            pdf.cell(0, 6, "Reporte oficial consolidado con verificación de integridad criptográfica SHA-256", ln=True, align="L")
            pdf.ln(4)

            # Tarjetas de resumen en el PDF
            pdf.set_fill_color(248, 250, 252)
            pdf.set_draw_color(226, 232, 240)
            pdf.rect(12, pdf.get_y(), 186, 18, "DF")

            y_card = pdf.get_y() + 4
            pdf.set_xy(16, y_card)
            pdf.set_font("Helvetica", "B", 11)
            pdf.set_text_color(31, 168, 255)
            pdf.cell(50, 5, f"Contactos Activos: {len(contacts)}", align="L")

            pdf.set_xy(75, y_card)
            pdf.set_font("Helvetica", "", 9)
            pdf.set_text_color(71, 85, 105)
            pdf.cell(60, 5, f"Almacenamiento: {stats['tamano_archivo_bytes']:,} Bytes", align="L")

            pdf.set_xy(135, y_card)
            pdf.set_font("Helvetica", "", 8)
            pdf.set_text_color(16, 185, 129)
            short_hash = (current_hash[:16] + "...") if current_hash else "N/A"
            pdf.cell(60, 5, f"SHA-256: {short_hash}", align="L")

            pdf.ln(16)

            # Cabecera de la tabla
            col_widths = [16, 50, 32, 54, 34]  # Total: 186 mm
            headers = ["ID", "Nombre", "Teléfono", "Correo", "Ciudad"]

            pdf.set_fill_color(31, 168, 255)
            pdf.set_draw_color(31, 168, 255)
            pdf.set_text_color(255, 255, 255)
            pdf.set_font("Helvetica", "B", 9)

            for i, h in enumerate(headers):
                pdf.cell(col_widths[i], 8, h, border=1, fill=True, align="C" if i == 0 else "L")
            pdf.ln()

            # Filas de la tabla
            pdf.set_font("Helvetica", "", 8)
            pdf.set_draw_color(241, 245, 249)

            for idx, c in enumerate(contacts):
                # Filas alternas con sombreado suave
                if idx % 2 == 0:
                    pdf.set_fill_color(255, 255, 255)
                else:
                    pdf.set_fill_color(248, 250, 252)

                pdf.set_text_color(15, 23, 42)

                # Celda ID
                pdf.cell(col_widths[0], 7, _safe_str(c.get("id", "")), border="B", fill=True, align="C")

                # Nombre (truncado seguro si excede)
                nom = _safe_str(str(c.get("nombre", ""))[:26])
                pdf.cell(col_widths[1], 7, nom, border="B", fill=True, align="L")

                # Teléfono
                tel = _safe_str(str(c.get("telefono", ""))[:18])
                pdf.cell(col_widths[2], 7, tel, border="B", fill=True, align="L")

                # Correo
                mail = _safe_str(str(c.get("correo", ""))[:32])
                pdf.cell(col_widths[3], 7, mail, border="B", fill=True, align="L")

                # Ciudad
                cd = _safe_str(str(c.get("ciudad", ""))[:18])
                pdf.cell(col_widths[4], 7, cd, border="B", fill=True, align="L")

                pdf.ln()

            pdf.output(str(out_path))

            msg = f"Reporte PDF generado exitosamente: {out_path.name}"
            logger.info(msg)
            return True, msg, str(out_path)

        except Exception as exc:
            logger.error("Error al generar PDF: %s", exc)
            return False, f"Fallo al generar PDF: {exc}", ""
