"""
Gestor de integridad criptográfica SHA-256 para ContactHub Enterprise.
Calcula y almacena el sello criptográfico de contactos.dat en contactos.sha256.
Detecta alteraciones no autorizadas, manipulación externa y corrupción de almacenamiento.
"""

import os
import hashlib
import logging
import tempfile
from pathlib import Path
from typing import Tuple

logger = logging.getLogger("storage.integrity")


class IntegrityManager:
    """
    Administrador del hash SHA-256 de integridad para el archivo de contactos.
    """

    def __init__(self, data_filepath: Path | str, hash_filepath: Path | str):
        self.data_filepath = Path(data_filepath)
        self.hash_filepath = Path(hash_filepath)

    def calculate_hash(self) -> str:
        """
        Calcula el hash SHA-256 de contactos.dat mediante streaming en bloques de 8192 bytes.
        Retorna la cadena hexadecimal de 64 caracteres.
        """
        if not self.data_filepath.exists():
            return ""

        sha = hashlib.sha256()
        try:
            with open(self.data_filepath, "rb") as f:
                while True:
                    chunk = f.read(8192)
                    if not chunk:
                        break
                    sha.update(chunk)
            return sha.hexdigest()
        except Exception as exc:
            logger.error("Error al calcular hash de %s: %s", self.data_filepath, exc)
            return ""

    def get_stored_hash(self) -> str:
        """Lee el hash guardado en contactos.sha256. Retorna cadena limpia o vacía."""
        if not self.hash_filepath.exists():
            return ""
        try:
            with open(self.hash_filepath, "r", encoding="utf-8") as f:
                return f.read().strip()
        except Exception as exc:
            logger.error("Error al leer el hash almacenado: %s", exc)
            return ""

    def save_hash(self) -> str:
        """
        Calcula el hash actual de contactos.dat y lo guarda atómicamente en contactos.sha256.
        Retorna el hash calculado y persistido.
        """
        current_hash = self.calculate_hash()
        try:
            self.hash_filepath.parent.mkdir(parents=True, exist_ok=True)
            temp_fd, temp_path = tempfile.mkstemp(
                dir=self.hash_filepath.parent,
                prefix="sha_tmp_",
                suffix=".sha256"
            )
            with os.fdopen(temp_fd, "w", encoding="utf-8") as f:
                f.write(current_hash)
            os.replace(temp_path, self.hash_filepath)
            logger.debug("Sello criptográfico SHA-256 actualizado: %s...", current_hash[:16])
            return current_hash
        except Exception as exc:
            logger.critical("Error al guardar el sello criptográfico: %s", exc)
            return ""

    def verify(self) -> Tuple[bool, str, str, str]:
        """
        Verifica la integridad del archivo comparando el hash almacenado con el hash real.
        
        Returns:
            Tuple[es_valido, hash_almacenado, hash_actual, mensaje_descriptivo]
        """
        if not self.data_filepath.exists():
            return True, "", "", "Archivo de datos no existe aún (sistema limpio)."

        current_hash = self.calculate_hash()
        stored_hash = self.get_stored_hash()

        if not stored_hash:
            # Si el archivo de hash no existe, se genera por primera vez
            self.save_hash()
            return True, current_hash, current_hash, "Sello criptográfico inicializado correctamente."

        if current_hash == stored_hash:
            return True, stored_hash, current_hash, "Integridad verificada al 100%. Sello SHA-256 auténtico."
        else:
            msg = (
                f"ALERTA DE SEGURIDAD: ¡El sello de integridad está ROTO! "
                f"Almacenado: {stored_hash[:16]}... vs Calculado: {current_hash[:16]}..."
            )
            logger.warning(msg)
            return False, stored_hash, current_hash, msg
