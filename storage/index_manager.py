"""
Gestor del índice primario para la Agenda de Contactos.

Mantiene un archivo JSON (indice.json) que mapea el ID de cada
contacto (como cadena) al número de registro (entero) en el archivo
de datos.  Esto permite búsquedas O(1) por ID sin recorrer todo
el archivo binario.

Operaciones de escritura se realizan de forma atómica: se escribe
primero a un archivo temporal y luego se renombra con os.replace().
"""

import os
import json
import logging
import tempfile

logger = logging.getLogger(__name__)


class IndexManager:
    """
    Gestiona el índice primario ID → número de registro.

    El índice se persiste en un archivo JSON con claves de tipo cadena
    (requisito de JSON) y valores enteros.
    """

    def __init__(self, filepath: str):
        """
        Inicializa el gestor de índice.

        Carga el índice existente del archivo, o inicializa uno vacío
        si el archivo no existe o está corrupto.

        Args:
            filepath: Ruta completa al archivo de índice JSON.
        """
        self.filepath = filepath
        self._index: dict[str, int] = self._load()

    def _load(self) -> dict:
        """
        Carga el índice desde el archivo JSON.

        Returns:
            Diccionario con el índice, o diccionario vacío si el
            archivo no existe o es inválido.
        """
        if not os.path.exists(self.filepath):
            logger.info(
                "Archivo de índice no encontrado, se inicia vacío: %s",
                self.filepath
            )
            return {}

        try:
            with open(self.filepath, 'r', encoding='utf-8') as f:
                data = json.load(f)

            if not isinstance(data, dict):
                logger.warning(
                    "Índice corrupto (no es un diccionario), se reinicia"
                )
                return {}

            # Asegurar que los valores sean enteros
            clean = {}
            for key, value in data.items():
                try:
                    clean[str(key)] = int(value)
                except (ValueError, TypeError):
                    logger.warning(
                        "Entrada inválida en índice: %s -> %s (omitida)",
                        key, value
                    )

            logger.info(
                "Índice cargado con %d entradas desde %s",
                len(clean), self.filepath
            )
            return clean

        except json.JSONDecodeError as exc:
            logger.warning(
                "Error al decodificar índice JSON (%s): %s",
                self.filepath, exc
            )
            return {}
        except (OSError, PermissionError) as exc:
            logger.warning(
                "Error al leer archivo de índice (%s): %s",
                self.filepath, exc
            )
            return {}

    def _save(self):
        """
        Guarda el índice en el archivo JSON de forma atómica.

        Escribe a un archivo temporal en el mismo directorio y luego
        usa os.replace() para hacer el reemplazo atómico.
        """
        try:
            directory = os.path.dirname(self.filepath)
            if directory:
                os.makedirs(directory, exist_ok=True)

            # Escritura atómica: escribir a temporal y renombrar
            fd, tmp_path = tempfile.mkstemp(
                dir=directory, suffix='.tmp', prefix='idx_'
            )
            try:
                with os.fdopen(fd, 'w', encoding='utf-8') as f:
                    json.dump(
                        self._index, f,
                        ensure_ascii=False,
                        indent=2,
                        sort_keys=True
                    )
                os.replace(tmp_path, self.filepath)
                logger.debug(
                    "Índice guardado con %d entradas", len(self._index)
                )
            except Exception:
                # Si falla la escritura, intentar limpiar el temporal
                try:
                    os.unlink(tmp_path)
                except OSError:
                    pass
                raise

        except (OSError, PermissionError) as exc:
            logger.error("Error al guardar índice: %s", exc)
            raise

    def add(self, contact_id: int, record_num: int):
        """
        Añade una entrada al índice y guarda.

        Args:
            contact_id: ID del contacto.
            record_num: Número de registro en el archivo de datos.
        """
        key = str(contact_id)
        self._index[key] = record_num
        self._save()
        logger.info(
            "Índice: añadida entrada ID=%s -> registro #%d",
            key, record_num
        )

    def get(self, contact_id: int) -> int | None:
        """
        Busca el número de registro para un ID de contacto.

        Args:
            contact_id: ID del contacto a buscar.

        Returns:
            Número de registro, o ``None`` si el ID no existe.
        """
        key = str(contact_id)
        result = self._index.get(key)
        if result is not None:
            logger.debug("Índice: ID=%s encontrado en registro #%d", key, result)
        else:
            logger.debug("Índice: ID=%s no encontrado", key)
        return result

    def remove(self, contact_id: int) -> bool:
        """
        Elimina una entrada del índice.

        Args:
            contact_id: ID del contacto a eliminar.

        Returns:
            ``True`` si se eliminó, ``False`` si no existía.
        """
        key = str(contact_id)
        if key in self._index:
            del self._index[key]
            self._save()
            logger.info("Índice: eliminada entrada ID=%s", key)
            return True
        logger.warning("Índice: intento de eliminar ID=%s inexistente", key)
        return False

    def has(self, contact_id: int) -> bool:
        """
        Verifica si un ID existe en el índice.

        Args:
            contact_id: ID a verificar.

        Returns:
            ``True`` si el ID existe, ``False`` en caso contrario.
        """
        return str(contact_id) in self._index

    def get_all(self) -> dict:
        """
        Devuelve una copia del índice completo.

        Returns:
            Diccionario {str_id: record_num}.
        """
        return dict(self._index)

    def get_all_ids(self) -> list[int]:
        """
        Devuelve una lista ordenada de todos los IDs en el índice.

        Returns:
            Lista de enteros ordenada ascendentemente.
        """
        try:
            return sorted(int(k) for k in self._index.keys())
        except ValueError:
            logger.warning("Hay claves no numéricas en el índice")
            ids = []
            for k in self._index.keys():
                try:
                    ids.append(int(k))
                except ValueError:
                    pass
            return sorted(ids)

    def rebuild(self, record_manager) -> int:
        """
        Reconstruye el índice completo desde el archivo de datos.

        Lee todos los registros del RecordManager y crea un nuevo
        índice basado en los IDs encontrados.

        Args:
            record_manager: Instancia de RecordManager.

        Returns:
            Número de registros indexados.
        """
        logger.info("Iniciando reconstrucción del índice...")

        old_count = len(self._index)
        self._index.clear()

        records = record_manager.read_all_records()
        indexed = 0

        for i, contact in enumerate(records):
            contact_id = contact.get('id', '').strip()
            if contact_id:
                self._index[str(contact_id)] = i
                indexed += 1

        self._save()

        logger.info(
            "Índice reconstruido: %d entradas (antes: %d)",
            indexed, old_count
        )
        return indexed

    def count(self) -> int:
        """
        Devuelve el número de entradas en el índice.

        Returns:
            Cantidad de entradas.
        """
        return len(self._index)
