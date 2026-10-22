import QtQuick 2.15
import QtQuick.Controls 2.15
import QtQuick.Layouts 1.15
import "../theme"
import "../components"

Item {
    id: root

    property var backupsList: []

    function reloadBackups() {
        root.backupsList = appController.listBackups();
    }

    Component.onCompleted: {
        reloadBackups();
    }

    Column {
        anchors.fill: parent
        anchors.margins: 24
        spacing: 16

        // ── Cabecera y Botón de Respaldo ─────────────────────────────────────
        Row {
            width: parent.width

            Column {
                width: parent.width - newBackupBtn.width - 20
                spacing: 4

                Text {
                    text: "Time Machine — Catálogo Histórico de Respaldos ZIP"
                    font.pixelSize: 20
                    font.weight: Font.Bold
                    font.family: Theme.fontFamily
                    color: Theme.textPrimary
                }

                Text {
                    text: "Empaquetado comprimido con DEFLATE de contactos.dat, indice.json y contactos.sha256"
                    font.pixelSize: 13
                    font.family: Theme.fontFamily
                    color: Theme.textSecondary
                }
            }

            HubButton {
                id: newBackupBtn
                text: "📦 Crear Nuevo Respaldo ZIP"
                variant: "primary"
                onClicked: {
                    var res = appController.createBackup("Respaldo manual desde Time Machine");
                    if (res.success) {
                        root.reloadBackups();
                    }
                }
            }
        }

        // ── Banner Informativo ───────────────────────────────────────────────
        Rectangle {
            width: parent.width
            height: 48
            radius: Theme.radiusSm
            color: Theme.bgElevated
            border.color: Theme.borderSubtle

            Row {
                anchors.centerIn: parent
                spacing: 32

                Text {
                    text: "Protocolo Safe Restore Activo"
                    font.pixelSize: 12; font.weight: Font.DemiBold; color: Theme.accentSuccess
                }

                Text {
                    text: "Algoritmo: ZIP DEFLATE (~60% de ahorro)"
                    font.pixelSize: 12; color: Theme.textSecondary
                }

                Text {
                    text: "Respaldos Disponibles: " + root.backupsList.length
                    font.pixelSize: 12; font.weight: Font.DemiBold; color: Theme.accentPrimary
                }
            }
        }

        // ── Lista Histórica de Respaldos ─────────────────────────────────────
        ListView {
            id: backupsView
            width: parent.width
            height: parent.height - 130
            clip: true
            spacing: 8
            model: root.backupsList

            delegate: Rectangle {
                width: backupsView.width
                height: 64
                radius: Theme.radiusSm
                color: Theme.bgCard
                border.color: Theme.borderSubtle
                border.width: 1

                Item {
                    anchors.fill: parent
                    anchors.margins: 14

                    Row {
                        anchors.left: parent.left
                        anchors.verticalCenter: parent.verticalCenter
                        spacing: 16

                        Rectangle {
                            width: 36
                            height: 36
                            radius: 8
                            color: Qt.rgba(139/255, 92/255, 246/255, 0.15)
                            anchors.verticalCenter: parent.verticalCenter

                            Text {
                                anchors.centerIn: parent
                                text: "📦"
                                font.pixelSize: 18
                            }
                        }

                        Column {
                            width: 320
                            anchors.verticalCenter: parent.verticalCenter
                            spacing: 2

                            Text {
                                text: modelData.filename
                                font.pixelSize: 13
                                font.weight: Font.Bold
                                font.family: "Consolas, monospace"
                                color: Theme.textPrimary
                            }

                            Text {
                                text: "Fecha: " + modelData.date + " (" + modelData.files_count + " archivos contenidos)"
                                font.pixelSize: 11
                                color: Theme.textMuted
                            }
                        }

                        Column {
                            width: 180
                            anchors.verticalCenter: parent.verticalCenter
                            spacing: 2

                            Text {
                                text: "Tamaño: " + modelData.size_formatted
                                font.pixelSize: 12
                                font.weight: Font.DemiBold
                                color: Theme.accentSuccess
                            }

                            Text {
                                text: "Original: " + (modelData.original_size ? modelData.original_size + " B" : "N/A")
                                font.pixelSize: 11
                                color: Theme.textSecondary
                            }
                        }
                    }

                    HubButton {
                        text: "Restaurar Copia"
                        variant: "warning"
                        anchors.right: parent.right
                        anchors.verticalCenter: parent.verticalCenter
                        onClicked: {
                            restoreDialog.targetZip = modelData.filename;
                            restoreDialog.open();
                        }
                    }
                }
            }
        }
    }

    // Diálogo de confirmación para Safe Restore
    HubDialog {
        id: restoreDialog
        property string targetZip: ""

        titleText: "Restaurar Respaldo"
        messageText: "¿Desea restaurar el estado del sistema desde '" + targetZip + "'? Antes de sobrescribir, el sistema creará automáticamente un respaldo de contingencia del estado actual."
        confirmText: "Restaurar"
        confirmVariant: "warning"
        onConfirmed: {
            appController.restoreBackup(targetZip);
            root.reloadBackups();
        }
    }
}
