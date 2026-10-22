"""
Gestor del índice primario en JSON para ContactHub Enterprise.
Mapea identificadores únicos (ID) al número ordinal de registro (0-based) en contactos.dat.
Permite búsquedas O(1) en RAM y persistencia atómica con tempfile + os.replace().
"""

import os
import json
import logging
import tempfile
from pathlib import Path
from typing import Dict, Optional, Any, List

logger = logging.getLogger("storage.index_manager")


class IndexManager:
    """
    Administrador del índice primario en memoria y en disco (data/indice.json).
    """

    def __init__(self, filepath: Path | str):
        self.filepath = Path(filepath)
        self._index: Dict[str, int] = {}
        self.load()

    def load(self) -> Dict[str, int]:
        """Carga el índice JSON desde disco. Si está corrupto o no existe, inicia vacío."""
        if not self.filepath.exists():
            logger.info("Archivo de índice no encontrado, se inicializa vacío: %s", self.filepath)
            self._index = {}
            return self._index

        try:
            with open(self.filepath, "r", encoding="utf-8") as f:
                raw_data = json.load(f)

            if not isinstance(raw_data, dict):
                logger.warning("Índice inválido (se esperaba JSON Object); se reinicia en memoria.")
                self._index = {}
                return self._index

            # Sanitización de datos: asegurar claves string y valores enteros
            clean_index = {}
            for k, v in raw_data.items():
                try:
                    clean_index[str(k).strip()] = int(v)
                except (ValueError, TypeError):
                    logger.warning("Entrada de índice corrupta omitida: %s -> %s", k, v)

            self._index = clean_index
            logger.info("Índice cargado exitosamente: %d entradas", len(self._index))
            return self._index

        except (json.JSONDecodeError, OSError) as exc:
            logger.error("Error al leer el archivo de índice %s: %s", self.filepath, exc)
            self._index = {}
            return self._index

    def save(self) -> bool:
        """
        Persiste el índice en disco de forma estrictamente atómica.
        Escribe a un archivo temporal en la misma carpeta y lo renombra con os.replace().
        """
        try:
            self.filepath.parent.mkdir(parents=True, exist_ok=True)
            temp_fd, temp_path = tempfile.mkstemp(
                dir=self.filepath.parent,
                prefix="idx_tmp_",
                suffix=".json"
            )
            with os.fdopen(temp_fd, "w", encoding="utf-8") as f:
                json.dump(self._index, f, indent=2, ensure_ascii=False)

            # Reemplazo atómico garantizado por el sistema operativo
            os.replace(temp_path, self.filepath)
            logger.debug("Índice persistido atómicamente (%d claves)", len(self._index))
            return True
        except Exception as exc:
            logger.critical("Error al guardar atómicamente el índice: %s", exc)
            return False

    def add(self, contact_id: Any, record_num: int) -> bool:
        """Asocia un ID con un número de registro y persiste en disco."""
        key = str(contact_id).strip()
        self._index[key] = int(record_num)
        return self.save()

    def get(self, contact_id: Any) -> Optional[int]:
        """Obtiene el número de registro para un ID en O(1) desde RAM."""
        key = str(contact_id).strip()
        return self._index.get(key)

    def has(self, contact_id: Any) -> bool:
        """Comprueba si un ID existe en el índice."""
        key = str(contact_id).strip()
        return key in self._index

    def remove(self, contact_id: Any) -> bool:
        """Elimina un ID del índice y actualiza el archivo en disco."""
        key = str(contact_id).strip()
        if key in self._index:
            del self._index[key]
            return self.save()
        return False

    def all(self) -> Dict[str, int]:
        """Retorna una copia superficial del índice completo en memoria."""
        return dict(self._index)

    def count(self) -> int:
        """Retorna el número de entradas en el índice."""
        return len(self._index)

    def clear(self) -> bool:
        """Limpia el índice en memoria y disco."""
        self._index = {}
        return self.save()

    def rebuild(self, records: List[Any]) -> int:
        """
        Reconstruye el índice a partir de una lista de tuplas (record_num, contact_dict).
        Solo incluye contactos cuyo estado sea 'A' (Activo).
        """
        new_index = {}
        for rec_num, contact in records:
            if isinstance(contact, dict) and contact.get("estado") == "A":
                c_id = str(contact.get("id", "")).strip()
                if c_id:
                    new_index[c_id] = int(rec_num)

        self._index = new_index
        self.save()
        logger.info("Índice reconstruido exitosamente con %d registros activos.", len(self._index))
        return len(self._index)
