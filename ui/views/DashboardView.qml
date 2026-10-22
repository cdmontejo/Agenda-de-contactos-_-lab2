import QtQuick 2.15
import QtQuick.Controls 2.15
import QtQuick.Layouts 1.15
import "../theme"
import "../components"

ScrollView {
    id: root

    contentWidth: availableWidth
    clip: true

    signal navigateTo(string viewName)
    signal openNewContactModal()

    Column {
        width: parent.width
        spacing: 20
        padding: 24

        // ── Banner de Bienvenida e Integridad ─────────────────────────────────
        Rectangle {
            width: parent.width - 48
            height: 84
            radius: Theme.radiusMd
            color: Theme.glassFill
            border.color: appController.isIntegrityValid ? Qt.rgba(16/255, 185/255, 129/255, 0.3) : Qt.rgba(239/255, 68/255, 68/255, 0.4)
            border.width: 1

            Row {
                anchors.fill: parent
                anchors.margins: 18
                spacing: 16

                Rectangle {
                    width: 48
                    height: 48
                    radius: 24
                    color: appController.isIntegrityValid ? Qt.rgba(16/255, 185/255, 129/255, 0.15) : Qt.rgba(239/255, 68/255, 68/255, 0.15)
                    anchors.verticalCenter: parent.verticalCenter

                    Text {
                        anchors.centerIn: parent
                        text: appController.isIntegrityValid ? "🛡️" : "⚠️"
                        font.pixelSize: 22
                    }
                }

                Column {
                    anchors.verticalCenter: parent.verticalCenter
                    width: parent.width - 240
                    spacing: 4

                    Text {
                        text: "Panel Ejecutivo — ContactHub Enterprise"
                        font.pixelSize: 16
                        font.weight: Font.Bold
                        font.family: Theme.fontFamily
                        color: Theme.textPrimary
                    }

                    Text {
                        text: appController.systemStatusMessage
                        font.pixelSize: 12
                        font.family: Theme.fontFamily
                        color: appController.isIntegrityValid ? Theme.textSecondary : Theme.accentDanger
                        elide: Text.ElideRight
                        width: parent.width
                    }
                }

                HubButton {
                    text: appController.isIntegrityValid ? "Sello Auténtico" : "Verificar Sello"
                    variant: appController.isIntegrityValid ? "success" : "danger"
                    anchors.verticalCenter: parent.verticalCenter
                    onClicked: root.navigateTo("integrity")
                }
            }
        }

        // ── Tarjetas Estadísticas Principales ────────────────────────────────
        Row {
            width: parent.width - 48
            spacing: 16

            StatCard {
                width: (parent.width - 48) / 4
                title: "Contactos Activos"
                value: appController.totalActiveContacts.toString()
                subtitle: "En índice primario O(1)"
                icon: "👥"
                accentColor: Theme.accentPrimary
            }

            StatCard {
                width: (parent.width - 48) / 4
                title: "Eliminados Lógicos"
                value: appController.totalDeletedContacts.toString()
                subtitle: "Marcados con byte 'D'"
                icon: "🗑️"
                accentColor: Theme.accentDanger
            }

            StatCard {
                width: (parent.width - 48) / 4
                title: "Registros en Disco"
                value: appController.totalPhysicalRecords.toString()
                subtitle: "Bloques de 256 bytes"
                icon: "💾"
                accentColor: Theme.accentPurple
            }

            StatCard {
                width: (parent.width - 48) / 4
                title: "Tamaño contactos.dat"
                value: appController.fileSizeFormatted
                subtitle: appController.fileSizeBytes + " Bytes en disco"
                icon: "⚡"
                accentColor: Theme.accentSuccess
            }
        }

        // ── Accesos Rápidos Ejecutivos ───────────────────────────────────────
        Text {
            text: "OPERACIONES RÁPIDAS"
            font.pixelSize: 12
            font.weight: Font.Bold
            font.family: Theme.fontFamily
            color: Theme.textSecondary
        }

        Row {
            width: parent.width - 48
            spacing: 14

            HubButton {
                text: "＋ Registrar Contacto"
                variant: "primary"
                onClicked: root.openNewContactModal()
            }

            HubButton {
                text: "🔍 Explorar Directorio"
                variant: "secondary"
                onClicked: root.navigateTo("contacts")
            }

            HubButton {
                text: "📑 Generar Reporte PDF"
                variant: "secondary"
                onClicked: appController.exportToPdf()
            }

            HubButton {
                text: "📦 Crear Respaldo ZIP"
                variant: "secondary"
                onClicked: appController.createBackup("Respaldo rápido desde Dashboard")
            }

            HubButton {
                text: "🌱 Sembrar Datos Demo"
                variant: "ghost"
                onClicked: appController.seedDemoData(10)
            }
        }

        // ── Especificación de Registros de 256 Bytes ──────────────────────────
        HubCard {
            width: parent.width - 48
            implicitHeight: 140

            Column {
                anchors.fill: parent
                spacing: 10

                Item {
                    width: parent.width
                    height: 18

                    Text {
                        anchors.left: parent.left
                        anchors.verticalCenter: parent.verticalCenter
                        text: "ARQUITECTURA DE PERSISTENCIA — REGISTRO INMUTABLE (256 BYTES)"
                        font.pixelSize: 12
                        font.weight: Font.Bold
                        font.family: Theme.fontFamily
                        color: Theme.accentPrimary
                    }

                    Text {
                        anchors.right: parent.right
                        anchors.verticalCenter: parent.verticalCenter
                        text: "Fórmula de Acceso: Offset = n × 256"
                        font.pixelSize: 11
                        font.family: "Consolas, monospace"
                        color: Theme.accentPurple
                    }
                }

                Text {
                    width: parent.width
                    text: "Cada contacto ocupa exactamente 256 bytes en 'contactos.dat' codificado en UTF-8 con espacios a la derecha (0x20). La búsqueda por ID consulta 'indice.json' en memoria en O(1) y navega directamente en disco con seek() sin escanear registros previos."
                    font.pixelSize: 12
                    font.family: Theme.fontFamily
                    color: Theme.textSecondary
                    wrapMode: Text.Wrap
                }

                Row {
                    spacing: 8
                    HubBadge { text: "ID: 10B"; status: "info" }
                    HubBadge { text: "Nombre: 80B"; status: "info" }
                    HubBadge { text: "Teléfono: 20B"; status: "info" }
                    HubBadge { text: "Correo: 80B"; status: "info" }
                    HubBadge { text: "Ciudad: 50B"; status: "info" }
                    HubBadge { text: "Estado: 1B ('A'/'D')"; status: "warning" }
                    HubBadge { text: "Padding: 14B"; status: "neutral" }
                    HubBadge { text: "Newline: 1B (\\n)"; status: "neutral" }
                }
            }
        }
    }
}
