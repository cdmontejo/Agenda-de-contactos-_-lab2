import QtQuick 2.15
import QtQuick.Controls 2.15
import QtQuick.Layouts 1.15
import "../theme"
import "../components"

ScrollView {
    id: root

    contentWidth: availableWidth
    clip: true

    Column {
        width: parent.width
        spacing: 20
        padding: 24

        // ── Cabecera de Integridad ───────────────────────────────────────────
        Column {
            spacing: 4
            Text {
                text: "Centro de Integridad Criptográfica y Sellos SHA-256"
                font.pixelSize: 20
                font.weight: Font.Bold
                font.family: Theme.fontFamily
                color: Theme.textPrimary
            }
            Text {
                text: "Monitoreo de inmutabilidad física, detección de modificaciones externas y validación de hash FIPS 180-4"
                font.pixelSize: 13
                font.family: Theme.fontFamily
                color: Theme.textSecondary
            }
        }

        // ── Estado del Sello Principal ───────────────────────────────────────
        Rectangle {
            width: parent.width - 48
            height: 110
            radius: Theme.radiusMd
            color: appController.isIntegrityValid
                   ? Qt.rgba(16/255, 185/255, 129/255, 0.12)
                   : Qt.rgba(239/255, 68/255, 68/255, 0.15)
            border.color: appController.isIntegrityValid
                          ? Theme.accentSuccess
                          : Theme.accentDanger
            border.width: 1.5

            Row {
                anchors.fill: parent
                anchors.margins: 20
                spacing: 20

                Rectangle {
                    width: 60
                    height: 60
                    radius: 30
                    color: appController.isIntegrityValid
                           ? Qt.rgba(16/255, 185/255, 129/255, 0.2)
                           : Qt.rgba(239/255, 68/255, 68/255, 0.2)
                    anchors.verticalCenter: parent.verticalCenter

                    Text {
                        anchors.centerIn: parent
                        text: appController.isIntegrityValid ? "✓" : "⚠"
                        font.pixelSize: 28
                        font.weight: Font.Bold
                        color: appController.isIntegrityValid ? Theme.accentSuccess : Theme.accentDanger
                    }
                }

                Column {
                    anchors.verticalCenter: parent.verticalCenter
                    width: parent.width - 240
                    spacing: 4

                    Text {
                        text: appController.isIntegrityValid
                              ? "SELLO DE INTEGRIDAD VÁLIDO Y AUTÉNTICO"
                              : "¡ALERTA CRÍTICA: SELLO CRIPTOGRÁFICO ROTO!"
                        font.pixelSize: 16
                        font.weight: Font.Bold
                        font.family: Theme.fontFamily
                        color: appController.isIntegrityValid ? Theme.accentSuccess : Theme.accentDanger
                    }

                    Text {
                        text: appController.systemStatusMessage
                        font.pixelSize: 12
                        font.family: Theme.fontFamily
                        color: Theme.textSecondary
                        wrapMode: Text.Wrap
                        width: parent.width
                    }
                }

                HubButton {
                    text: "Verificar Ahora"
                    variant: "primary"
                    anchors.verticalCenter: parent.verticalCenter
                    onClicked: appController.verifyIntegrity()
                }
            }
        }

        // ── Tarjetas de Comparación de Hash SHA-256 ──────────────────────────
        Row {
            width: parent.width - 48
            spacing: 16

            HubCard {
                width: (parent.width - 16) / 2
                implicitHeight: 140

                Column {
                    anchors.fill: parent
                    spacing: 8

                    Item {
                        width: parent.width
                        height: 22

                        Text {
                            anchors.left: parent.left
                            anchors.verticalCenter: parent.verticalCenter
                            text: "HASH ALMACENADO (contactos.sha256)"
                            font.pixelSize: 11
                            font.weight: Font.Bold
                            color: Theme.accentPrimary
                        }
                        HubBadge {
                            anchors.right: parent.right
                            anchors.verticalCenter: parent.verticalCenter
                            text: "Persistido en Disco"
                            status: "info"
                        }
                    }

                    Rectangle {
                        width: parent.width
                        height: 50
                        radius: Theme.radiusSm
                        color: Theme.bgInput
                        border.color: Theme.borderSubtle

                        Text {
                            anchors.centerIn: parent
                            width: parent.width - 20
                            text: appController.storedHash || "Sin sello registrado"
                            font.pixelSize: 12
                            font.family: "Consolas, monospace"
                            color: Theme.textPrimary
                            wrapMode: Text.WrapAnywhere
                        }
                    }

                    Text {
                        text: "Último hash validado y guardado durante la última operación de escritura autorizada."
                        font.pixelSize: 11
                        color: Theme.textMuted
                    }
                }
            }

            HubCard {
                width: (parent.width - 16) / 2
                implicitHeight: 140

                Column {
                    anchors.fill: parent
                    spacing: 8

                    Item {
                        width: parent.width
                        height: 22

                        Text {
                            anchors.left: parent.left
                            anchors.verticalCenter: parent.verticalCenter
                            text: "HASH CALCULADO EN VIVO (contactos.dat)"
                            font.pixelSize: 11
                            font.weight: Font.Bold
                            color: appController.isIntegrityValid ? Theme.accentSuccess : Theme.accentDanger
                        }
                        HubBadge {
                            anchors.right: parent.right
                            anchors.verticalCenter: parent.verticalCenter
                            text: appController.isIntegrityValid ? "Coincidencia Exacta" : "Discrepancia"
                            status: appController.isIntegrityValid ? "ok" : "error"
                        }
                    }

                    Rectangle {
                        width: parent.width
                        height: 50
                        radius: Theme.radiusSm
                        color: Theme.bgInput
                        border.color: appController.isIntegrityValid ? Theme.borderSubtle : Theme.accentDanger

                        Text {
                            anchors.centerIn: parent
                            width: parent.width - 20
                            text: appController.calculatedHash || "Calculando hash..."
                            font.pixelSize: 12
                            font.family: "Consolas, monospace"
                            color: appController.isIntegrityValid ? Theme.textPrimary : Theme.accentDanger
                            wrapMode: Text.WrapAnywhere
                        }
                    }

                    Text {
                        text: "Resultado del escaneo en streaming (bloques de 8192 bytes) del archivo físico real."
                        font.pixelSize: 11
                        color: Theme.textMuted
                    }
                }
            }
        }

        // ── Panel de Acciones de Seguridad y Laboratorio ──────────────────────
        Text {
            text: "ACCIONES DE SEGURIDAD Y DIAGNÓSTICO DE LABORATORIO"
            font.pixelSize: 12
            font.weight: Font.Bold
            color: Theme.textSecondary
        }

        Row {
            width: parent.width - 48
            spacing: 12

            HubButton {
                text: "🛠️ Reconstruir Índice indice.json"
                variant: "secondary"
                onClicked: appController.rebuildIndex()
            }

            HubButton {
                text: "🔏 Re-firmar Sello Actual"
                variant: "secondary"
                onClicked: appController.repairSeal()
            }

            HubButton {
                text: "🧪 Simular Alteración de Byte (Tamper)"
                variant: "danger"
                onClicked: appController.tamperDataForDemo()
            }
        }

        // ── Explicación Técnica de Sellos SHA-256 ─────────────────────────────
        HubCard {
            width: parent.width - 48
            implicitHeight: 180

            Column {
                anchors.fill: parent
                spacing: 10

                Text {
                    text: "¿CÓMO FUNCIONA EL SELLO Y CÓMO SE ROMPERÍA LA INTEGRIDAD?"
                    font.pixelSize: 12
                    font.weight: Font.Bold
                    color: Theme.accentPrimary
                }

                Text {
                    width: parent.width
                    text: "• Algoritmo Criptográfico: Usamos SHA-256 (FIPS 180-4). Genera una huella de 256 bits (64 caracteres hexadecimales) de 'contactos.dat'.\n• Efecto Avalancha: Cambiar un solo bit en cualquier campo (incluso en un espacio de relleno de 256B) altera más del 50% del hash final.\n• Escenarios donde se rompe el sello:\n    1. Edición manual de 'contactos.dat' con un editor externo (Notepad, VS Code).\n    2. Caída del sistema antes de flush() durante una escritura binaria.\n    3. Modificación del byte de estado sin pasar por la aplicación.\n    4. Corrupción de sectores o manipulación intencionada de registros.\n• Auto-Sanación: Si se detecta alteración, el sistema permite restaurar desde el Time Machine de respaldos ZIP o re-firmar el sello tras una auditoría manual."
                    font.pixelSize: 12
                    font.family: Theme.fontFamily
                    color: Theme.textSecondary
                    wrapMode: Text.Wrap
                }
            }
        }
    }
}
