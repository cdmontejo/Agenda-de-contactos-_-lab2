"""
Gestor de integridad SHA-256 para la Agenda de Contactos.

Calcula y verifica el hash SHA-256 del archivo de datos para
detectar modificaciones no autorizadas o corrupción.

El hash se almacena en un archivo de texto (.sha256) y se actualiza
cada vez que se modifica el archivo de datos a través de la
aplicación.
"""

import os
import hashlib
import logging
import tempfile

logger = logging.getLogger(__name__)


class IntegrityManager:
    """
    Gestiona la verificación de integridad del archivo de datos
    mediante hash SHA-256.
    """

    def __init__(self, data_filepath: str, hash_filepath: str):
        """
        Inicializa el gestor de integridad.

        Args:
            data_filepath: Ruta al archivo de datos (contactos.dat).
            hash_filepath: Ruta al archivo de hash (contactos.sha256).
        """
        self.data_filepath = data_filepath
        self.hash_filepath = hash_filepath

    def calculate_hash(self) -> str:
        """
        Calcula el hash SHA-256 del archivo de datos.

        Lee el archivo en bloques de 8192 bytes para manejar archivos
        grandes de forma eficiente.

        Returns:
            Cadena hexadecimal del hash SHA-256, o cadena vacía si
            el archivo no existe.
        """
        if not os.path.exists(self.data_filepath):
            logger.warning(
                "Archivo de datos no encontrado para calcular hash: %s",
                self.data_filepath
            )
            return ""

        try:
            sha256 = hashlib.sha256()
            with open(self.data_filepath, 'rb') as f:
                while True:
                    chunk = f.read(8192)
                    if not chunk:
                        break
                    sha256.update(chunk)

            digest = sha256.hexdigest()
            logger.debug("Hash SHA-256 calculado: %s", digest[:16] + "...")
            return digest

        except (OSError, PermissionError) as exc:
            logger.error("Error al calcular hash: %s", exc)
            return ""

    def save_hash(self):
        """
        Calcula el hash actual y lo guarda en el archivo de hash.

        La escritura se realiza de forma atómica: se escribe a un
        archivo temporal y luego se renombra.
        """
        current_hash = self.calculate_hash()
        if not current_hash:
            logger.warning(
                "No se pudo calcular el hash, no se guarda"
            )
            return

        try:
            directory = os.path.dirname(self.hash_filepath)
            if directory:
                os.makedirs(directory, exist_ok=True)

            # Escritura atómica
            fd, tmp_path = tempfile.mkstemp(
                dir=directory, suffix='.tmp', prefix='hash_'
            )
            try:
                with os.fdopen(fd, 'w', encoding='utf-8') as f:
                    f.write(current_hash)
                os.replace(tmp_path, self.hash_filepath)
                logger.info("Hash SHA-256 guardado en %s", self.hash_filepath)
            except Exception:
                try:
                    os.unlink(tmp_path)
                except OSError:
                    pass
                raise

        except (OSError, PermissionError) as exc:
            logger.error("Error al guardar hash: %s", exc)

    def load_stored_hash(self) -> str | None:
        """
        Lee el hash almacenado en el archivo de hash.

        Returns:
            Cadena con el hash almacenado, o ``None`` si el archivo
            no existe o no se puede leer.
        """
        if not os.path.exists(self.hash_filepath):
            logger.info("Archivo de hash no encontrado: %s", self.hash_filepath)
            return None

        try:
            with open(self.hash_filepath, 'r', encoding='utf-8') as f:
                stored = f.read().strip()
            logger.debug("Hash almacenado leído: %s", stored[:16] + "...")
            return stored

        except (OSError, PermissionError, UnicodeDecodeError) as exc:
            logger.error("Error al leer hash almacenado: %s", exc)
            return None

    def verify(self) -> tuple[bool, str]:
        """
        Verifica la integridad del archivo de datos.

        Compara el hash SHA-256 actual del archivo de datos con el
        hash almacenado previamente.

        Returns:
            Tupla (éxito, mensaje):
              - (True,  mensaje) si los hashes coinciden
              - (False, mensaje) si hay discrepancia o error
        """
        # Caso 1: no existe el archivo de datos
        if not os.path.exists(self.data_filepath):
            file_size = 0
            try:
                if os.path.exists(self.data_filepath):
                    file_size = os.path.getsize(self.data_filepath)
            except OSError:
                pass

            if file_size == 0 and os.path.exists(self.data_filepath):
                # Archivo vacío es válido
                return (True, "Archivo de datos vacío, integridad correcta")

            return (False, "Archivo de datos no encontrado")

        # Caso 1b: archivo de datos vacío
        try:
            if os.path.getsize(self.data_filepath) == 0:
                return (True, "Archivo de datos vacío, integridad correcta")
        except OSError:
            pass

        # Caso 2: no existe el archivo de hash
        stored_hash = self.load_stored_hash()
        if stored_hash is None:
            return (
                False,
                "Archivo de hash no encontrado. Se recomienda "
                "recalcular con 'Actualizar hash'"
            )

        # Caso 3: calcular y comparar
        current_hash = self.calculate_hash()
        if not current_hash:
            return (False, "No se pudo calcular el hash actual")

        if current_hash == stored_hash:
            logger.info("Verificación de integridad exitosa")
            return (
                True,
                "Integridad verificada correctamente. "
                f"SHA-256: {current_hash[:16]}..."
            )
        else:
            logger.warning(
                "¡Discrepancia de integridad! "
                "Almacenado: %s... Actual: %s...",
                stored_hash[:16], current_hash[:16]
            )
            return (
                False,
                f"¡ALERTA! Hash no coincide.\n"
                f"  Almacenado: {stored_hash[:16]}...\n"
                f"  Actual:     {current_hash[:16]}...\n"
                f"El archivo pudo haber sido modificado externamente."
            )

    def update(self):
        """
        Recalcula y guarda el hash del archivo de datos.

        Alias de ``save_hash()`` para uso semántico más claro.
        """
        self.save_hash()
