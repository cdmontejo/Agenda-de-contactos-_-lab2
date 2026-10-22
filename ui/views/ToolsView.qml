import QtQuick 2.15
import QtQuick.Controls 2.15
import QtQuick.Layouts 1.15
import "../theme"
import "../components"

ScrollView {
    id: root

    contentWidth: availableWidth
    clip: true

    property var sysInfo: ({})
    property var logLines: []

    function refreshData() {
        root.sysInfo = appController.getSystemInfo();
        root.logLines = appController.getRecentLogs(60);
    }

    Component.onCompleted: {
        refreshData();
    }

    Column {
        width: parent.width
        spacing: 20
        padding: 24

        Column {
            spacing: 4
            Text {
                text: "Herramientas del Sistema y Telemetría"
                font.pixelSize: 20
                font.weight: Font.Bold
                font.family: Theme.fontFamily
                color: Theme.textPrimary
            }
            Text {
                text: "Diagnóstico de hardware, estado del archivo físico de registros y visor en vivo de logs"
                font.pixelSize: 13
                font.family: Theme.fontFamily
                color: Theme.textSecondary
            }
        }

        // ── Tarjeta de Diagnóstico del Archivo Binario ────────────────────────
        HubCard {
            width: parent.width - 48
            implicitHeight: 160

            Column {
                anchors.fill: parent
                spacing: 12

                Text {
                    text: "MÉTRICAS FÍSICAS DEL ARCHIVO DE REGISTROS (contactos.dat)"
                    font.pixelSize: 11
                    font.weight: Font.Bold
                    color: Theme.accentPrimary
                }

                Row {
                    width: parent.width
                    spacing: 20

                    Column {
                        spacing: 2
                        Text { text: "TAMAÑO DE REGISTRO"; font.pixelSize: 10; color: Theme.textMuted }
                        Text { text: "256 Bytes Estrictos"; font.pixelSize: 14; font.weight: Font.Bold; color: Theme.accentSuccess }
                    }

                    Rectangle { width: 1; height: 32; color: Theme.borderSubtle }

                    Column {
                        spacing: 2
                        Text { text: "TOTAL DE REGISTROS"; font.pixelSize: 10; color: Theme.textMuted }
                        Text { text: (root.sysInfo.totalRecords || 0) + " Bloques"; font.pixelSize: 14; font.weight: Font.Bold; color: Theme.textPrimary }
                    }

                    Rectangle { width: 1; height: 32; color: Theme.borderSubtle }

                    Column {
                        spacing: 2
                        Text { text: "TAMAÑO FÍSICO EN DISCO"; font.pixelSize: 10; color: Theme.textMuted }
                        Text { text: (root.sysInfo.fileSizeBytes || 0) + " Bytes"; font.pixelSize: 14; font.weight: Font.Bold; color: Theme.accentPurple }
                    }

                    Rectangle { width: 1; height: 32; color: Theme.borderSubtle }

                    Column {
                        spacing: 2
                        Text { text: "VERSIÓN DE PYTHON"; font.pixelSize: 10; color: Theme.textMuted }
                        Text { text: "Python " + (root.sysInfo.pythonVersion || "3.14"); font.pixelSize: 14; font.weight: Font.Bold; color: Theme.textSecondary }
                    }
                }

                Text {
                    text: "Ruta del Archivo: " + (root.sysInfo.dataFile || "")
                    font.pixelSize: 11
                    font.family: "Consolas, monospace"
                    color: Theme.textMuted
                    elide: Text.ElideMiddle
                    width: parent.width
                }
            }
        }

        // ── Visor de Logs del Sistema (app.log) ───────────────────────────────
        HubCard {
            width: parent.width - 48
            implicitHeight: 300

            Column {
                anchors.fill: parent
                spacing: 10

                Item {
                    width: parent.width
                    height: 28

                    Text {
                        anchors.left: parent.left
                        anchors.verticalCenter: parent.verticalCenter
                        text: "REGISTRO EN VIVO DE OPERACIONES (logs/app.log)"
                        font.pixelSize: 11
                        font.weight: Font.Bold
                        color: Theme.accentPrimary
                    }

                    HubButton {
                        anchors.right: parent.right
                        anchors.verticalCenter: parent.verticalCenter
                        text: "🔄 Actualizar Logs"
                        variant: "ghost"
                        implicitHeight: 28
                        onClicked: root.refreshData()
                    }
                }

                Rectangle {
                    width: parent.width
                    height: 220
                    radius: Theme.radiusSm
                    color: "#050A14"
                    border.color: Theme.borderSubtle

                    ScrollView {
                        anchors.fill: parent
                        anchors.margins: 10
                        clip: true

                        TextArea {
                            readOnly: true
                            text: root.logLines.join("\n")
                            font.family: "Consolas, 'Courier New', monospace"
                            font.pixelSize: 11
                            color: "#A7F3D0"
                            selectByMouse: true
                            background: null
                        }
                    }
                }
            }
        }
    }
}
