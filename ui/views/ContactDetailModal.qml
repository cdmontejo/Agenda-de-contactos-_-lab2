import QtQuick 2.15
import QtQuick.Controls 2.15
import "../theme"
import "../components"

Dialog {
    id: root

    property var contactData: null
    property var inspectionData: null

    modal: true
    dim: true
    anchors.centerIn: parent
    implicitWidth: 680
    implicitHeight: 520
    closePolicy: Dialog.CloseOnEscape | Dialog.CloseOnPressOutside

    background: Rectangle {
        radius: Theme.radiusMd
        color: Theme.bgSurface
        border.color: Theme.borderSubtle
        border.width: 1
    }

    contentItem: Item {
        anchors.fill: parent
        anchors.margins: 20

        Column {
            anchors.fill: parent
            spacing: 14

            // Cabecera del modal
            Row {
                width: parent.width

                Column {
                    width: parent.width - closeBtn.width
                    spacing: 2

                    Text {
                        text: "Inspección Profunda de Registro Binario"
                        font.pixelSize: 17
                        font.weight: Font.Bold
                        font.family: Theme.fontFamily
                        color: Theme.textPrimary
                    }

                    Text {
                        text: "Verificación de acceso aleatorio directo O(1), seek(), tell() y estructura de 256 bytes"
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

            // Barra de estado de acceso aleatorio directo
            Rectangle {
                width: parent.width
                height: 54
                radius: Theme.radiusSm
                color: Theme.bgElevated
                border.color: Theme.borderSubtle

                Row {
                    anchors.centerIn: parent
                    spacing: 24

                    Column {
                        Text { text: "REGISTRO #"; font.pixelSize: 9; font.weight: Font.Bold; color: Theme.textMuted }
                        Text {
                            text: root.inspectionData ? "#" + root.inspectionData.record_num : "N/A"
                            font.pixelSize: 14; font.weight: Font.Bold; color: Theme.accentPrimary
                        }
                    }

                    Rectangle { width: 1; height: 30; color: Theme.borderSubtle; anchors.verticalCenter: parent.verticalCenter }

                    Column {
                        Text { text: "BYTE OFFSET (seek)"; font.pixelSize: 9; font.weight: Font.Bold; color: Theme.textMuted }
                        Text {
                            text: root.inspectionData ? root.inspectionData.byte_offset + " Bytes" : "N/A"
                            font.pixelSize: 14; font.weight: Font.Bold; color: Theme.accentSuccess
                        }
                    }

                    Rectangle { width: 1; height: 30; color: Theme.borderSubtle; anchors.verticalCenter: parent.verticalCenter }

                    Column {
                        Text { text: "FÓRMULAseek()"; font.pixelSize: 9; font.weight: Font.Bold; color: Theme.textMuted }
                        Text {
                            text: root.inspectionData ? root.inspectionData.record_num + " × 256 = " + root.inspectionData.byte_offset : "N/A"
                            font.pixelSize: 13; font.family: "Consolas, monospace"; color: Theme.accentPurple
                        }
                    }

                    Rectangle { width: 1; height: 30; color: Theme.borderSubtle; anchors.verticalCenter: parent.verticalCenter }

                    Column {
                        Text { text: "tell() ANTES / DESPUÉS"; font.pixelSize: 9; font.weight: Font.Bold; color: Theme.textMuted }
                        Text {
                            text: root.inspectionData ? root.inspectionData.tell_antes + " / " + root.inspectionData.tell_despues : "N/A"
                            font.pixelSize: 13; font.family: "Consolas, monospace"; color: Theme.textPrimary
                        }
                    }
                }
            }

            // Datos del contacto en tarjetas limpias
            Row {
                width: parent.width
                spacing: 12

                Rectangle {
                    width: (parent.width - 12) / 2
                    height: 110
                    radius: Theme.radiusSm
                    color: Theme.bgInput
                    border.color: Theme.borderSubtle

                    Column {
                        anchors.fill: parent
                        anchors.margins: 12
                        spacing: 6

                        Text {
                            text: "DATOS DEL CONTACTO"
                            font.pixelSize: 10
                            font.weight: Font.Bold
                            color: Theme.accentPrimary
                        }

                        Text {
                            text: "ID: " + (root.contactData ? root.contactData.id : "")
                            font.pixelSize: 12; font.weight: Font.DemiBold; color: Theme.textPrimary
                        }

                        Text {
                            text: "Nombre: " + (root.contactData ? root.contactData.nombre : "")
                            font.pixelSize: 12; color: Theme.textPrimary; elide: Text.ElideRight; width: parent.width
                        }

                        Text {
                            text: "Ciudad: " + (root.contactData ? root.contactData.ciudad : "")
                            font.pixelSize: 12; color: Theme.textSecondary
                        }
                    }
                }

                Rectangle {
                    width: (parent.width - 12) / 2
                    height: 110
                    radius: Theme.radiusSm
                    color: Theme.bgInput
                    border.color: Theme.borderSubtle

                    Column {
                        anchors.fill: parent
                        anchors.margins: 12
                        spacing: 6

                        Text {
                            text: "COMUNICACIÓN Y ESTADO"
                            font.pixelSize: 10
                            font.weight: Font.Bold
                            color: Theme.accentPurple
                        }

                        Text {
                            text: "Teléfono: " + (root.contactData ? root.contactData.telefono : "")
                            font.pixelSize: 12; color: Theme.textPrimary
                        }

                        Text {
                            text: "Correo: " + (root.contactData ? root.contactData.correo : "")
                            font.pixelSize: 12; color: Theme.textPrimary; elide: Text.ElideRight; width: parent.width
                        }

                        Row {
                            spacing: 8
                            Text { text: "Estado en Disco:"; font.pixelSize: 12; color: Theme.textSecondary }
                            HubBadge {
                                text: root.contactData && root.contactData.estado === "A" ? "Activo (A)" : "Eliminado (D)"
                                status: root.contactData && root.contactData.estado === "A" ? "ok" : "error"
                            }
                        }
                    }
                }
            }

            // Visor Hexadecimal de los 256 bytes
            Text {
                text: "VOLCADO HEXADECIMAL DEL REGISTRO EN DISCO (256 BYTES EXACTOS):"
                font.pixelSize: 10
                font.weight: Font.Bold
                font.family: Theme.fontFamily
                color: Theme.textSecondary
            }

            Rectangle {
                width: parent.width
                height: 180
                radius: Theme.radiusSm
                color: "#050A14"
                border.color: Theme.borderSubtle

                ScrollView {
                    anchors.fill: parent
                    anchors.margins: 10
                    clip: true

                    TextArea {
                        readOnly: true
                        text: root.inspectionData ? root.inspectionData.hex_dump : "Cargando volcado hexadecimal..."
                        font.family: "Consolas, 'Courier New', monospace"
                        font.pixelSize: 11
                        color: "#38BDF8"
                        selectByMouse: true
                        background: null
                    }
                }
            }
        }
    }
}

