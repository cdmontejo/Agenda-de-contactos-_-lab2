import QtQuick 2.15
import QtQuick.Controls 2.15
import "../theme"
import "../components"

Dialog {
    id: root

    property bool isEdit: false
    property string initialId: ""
    property string initialNombre: ""
    property string initialTelefono: ""
    property string initialCorreo: ""
    property string initialCiudad: ""

    signal saved()

    modal: true
    dim: true
    anchors.centerIn: parent
    implicitWidth: 480
    implicitHeight: 520
    closePolicy: Dialog.CloseOnEscape | Dialog.CloseOnPressOutside

    background: Rectangle {
        radius: Theme.radiusMd
        color: Theme.bgSurface
        border.color: Theme.borderSubtle
        border.width: 1
    }

    onOpened: {
        idField.text = root.initialId;
        nombreField.text = root.initialNombre;
        telefonoField.text = root.initialTelefono;
        correoField.text = root.initialCorreo;
        ciudadField.text = root.initialCiudad;
        if (!root.isEdit) {
            idField.forceActiveFocus();
        } else {
            nombreField.forceActiveFocus();
        }
    }

    contentItem: Item {
        anchors.fill: parent
        anchors.margins: 20

        Column {
            anchors.fill: parent
            spacing: 12

            // Cabecera
            Row {
                width: parent.width

                Column {
                    width: parent.width - closeBtn.width
                    spacing: 2

                    Text {
                        text: root.isEdit ? "Editar Contacto In-Place" : "Nuevo Contacto Empresarial"
                        font.pixelSize: 17
                        font.weight: Font.Bold
                        font.family: Theme.fontFamily
                        color: Theme.textPrimary
                    }

                    Text {
                        text: root.isEdit
                              ? "Sobrescribe exactamente 256 bytes en su posición física en contactos.dat"
                              : "Registra en disco calculando offset = N × 256 con seek() y tell()"
                        font.pixelSize: 11
                        font.family: Theme.fontFamily
                        color: Theme.textMuted
                    }
                }

                HubButton {
                    id: closeBtn
                    text: "✕"
                    variant: "ghost"
                    implicitWidth: 32
                    implicitHeight: 32
                    onClicked: root.close()
                }
            }

            Rectangle { width: parent.width; height: 1; color: Theme.borderSubtle }

            // Campos del formulario
            HubTextField {
                id: idField
                width: parent.width
                label: "ID del Contacto (Entero Único)"
                placeholderText: "Ej. 101"
                readOnly: root.isEdit
                maxBytes: 10
            }

            HubTextField {
                id: nombreField
                width: parent.width
                label: "Nombre Completo (Soporta UTF-8 y Acentos)"
                placeholderText: "Ej. Ángel María Peña González"
                maxBytes: 80
            }

            HubTextField {
                id: telefonoField
                width: parent.width
                label: "Número de Teléfono"
                placeholderText: "Ej. +502 5555-1234"
                maxBytes: 20
            }

            HubTextField {
                id: correoField
                width: parent.width
                label: "Correo Electrónico"
                placeholderText: "Ej. angel.pena@empresa.com.gt"
                maxBytes: 80
            }

            HubTextField {
                id: ciudadField
                width: parent.width
                label: "Ciudad de Residencia"
                placeholderText: "Ej. Quetzaltenango"
                maxBytes: 50
            }

            Item { width: 1; height: 8 }

            // Botones de acción
            Row {
                anchors.right: parent.right
                spacing: 10

                HubButton {
                    text: "Cancelar"
                    variant: "secondary"
                    onClicked: root.close()
                }

                HubButton {
                    text: root.isEdit ? "Guardar Cambios In-Place" : "Registrar Contacto"
                    variant: "primary"
                    onClicked: {
                        var res;
                        if (root.isEdit) {
                            res = appController.updateContact(
                                idField.text,
                                nombreField.text,
                                telefonoField.text,
                                correoField.text,
                                ciudadField.text
                            );
                        } else {
                            res = appController.addContact(
                                idField.text,
                                nombreField.text,
                                telefonoField.text,
                                correoField.text,
                                ciudadField.text
                            );
                        }
                        if (res.success) {
                            root.saved();
                            root.close();
                        }
                    }
                }
            }
        }
    }
}
