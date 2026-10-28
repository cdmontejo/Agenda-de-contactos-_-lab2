"""
Modelo de datos reactivo para Qt Quick (QAbstractListModel).
Conecta la colección de contactos en memoria con los componentes ListView / TableView de QML
mediante roles fuertemente tipados y virtualización de elementos gráficos.
"""

from typing import List, Dict, Any, Optional
from PySide6.QtCore import QAbstractListModel, QModelIndex, Qt, QByteArray


class ContactListModel(QAbstractListModel):
    """
    Modelo de lista para QML con roles específicos para campos y metadatos de persistencia binaria.
    """

    IdRole = Qt.UserRole + 1
    NombreRole = Qt.UserRole + 2
    TelefonoRole = Qt.UserRole + 3
    CorreoRole = Qt.UserRole + 4
    CiudadRole = Qt.UserRole + 5
    EstadoRole = Qt.UserRole + 6
    OffsetRole = Qt.UserRole + 7
    RecordNumRole = Qt.UserRole + 8

    def __init__(self, parent=None):
        super().__init__(parent)
        self._contacts: List[Dict[str, Any]] = []

    def rowCount(self, parent=QModelIndex()) -> int:
        return len(self._contacts)

    def data(self, index: QModelIndex, role: int = Qt.DisplayRole) -> Any:
        if not index.isValid() or not (0 <= index.row() < len(self._contacts)):
            return None

        contact = self._contacts[index.row()]

        if role == self.IdRole:
            return contact.get("id", "")
        elif role == self.NombreRole:
            return contact.get("nombre", "")
        elif role == self.TelefonoRole:
            return contact.get("telefono", "")
        elif role == self.CorreoRole:
            return contact.get("correo", "")
        elif role == self.CiudadRole:
            return contact.get("ciudad", "")
        elif role == self.EstadoRole:
            return contact.get("estado", "A")
        elif role == self.OffsetRole:
            return contact.get("byte_offset", 0)
        elif role == self.RecordNumRole:
            return contact.get("record_num", 0)

        return None

    def roleNames(self) -> Dict[int, QByteArray]:
        return {
            self.IdRole: QByteArray(b"id"),
            self.NombreRole: QByteArray(b"nombre"),
            self.TelefonoRole: QByteArray(b"telefono"),
            self.CorreoRole: QByteArray(b"correo"),
            self.CiudadRole: QByteArray(b"ciudad"),
            self.EstadoRole: QByteArray(b"estado"),
            self.OffsetRole: QByteArray(b"byteOffset"),
            self.RecordNumRole: QByteArray(b"recordNum"),
        }

    def set_contacts(self, contacts: List[Dict[str, Any]]) -> None:
        """Reemplaza la colección de contactos emitiendo las señales requeridas por Qt."""
        self.beginResetModel()
        self._contacts = list(contacts)
        self.endResetModel()

    def get_contact_at(self, row: int) -> Optional[Dict[str, Any]]:
        """Retorna el diccionario de contacto en una posición específica."""
        if 0 <= row < len(self._contacts):
            return dict(self._contacts[row])
        return None

    def clear(self) -> None:
        """Limpia el modelo."""
        self.beginResetModel()
        self._contacts = []
        self.endResetModel()

