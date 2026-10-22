import QtQuick 2.15
import QtQuick.Controls 2.15
import QtQuick.Layouts 1.15
import "../theme"
import "../components"

ScrollView {
    id: root

    contentWidth: availableWidth
    clip: true

    property var previewData: null
    property var importSummary: null

    Column {
        width: parent.width
        spacing: 20
        padding: 24

        Column {
            spacing: 4
            Text {
                text: "Importación Inteligente desde CSV"
                font.pixelSize: 20
                font.weight: Font.Bold
                font.family: Theme.fontFamily
                color: Theme.textPrimary
            }
            Text {
                text: "Proceso asistido de 3 pasos: selección de archivo, vista previa y validación, e inserción transaccional"
                font.pixelSize: 13
                font.family: Theme.fontFamily
                color: Theme.textSecondary
            }
        }

        // ── Paso 1: Selección de Archivo ──────────────────────────────────────
        HubCard {
            width: parent.width - 48
            implicitHeight: 120

            Column {
                anchors.fill: parent
                spacing: 12

                Text {
                    text: "PASO 1: ESPECIFICAR RUTA DEL ARCHIVO CSV"
                    font.pixelSize: 11
                    font.weight: Font.Bold
                    color: Theme.accentPrimary
                }

                Row {
                    width: parent.width
                    spacing: 12

                    HubTextField {
                        id: csvPathInput
                        width: parent.width - previewBtn.width - 12
                        placeholderText: "Ejemplo: C:/contactos.csv o exports/contactos_demo.csv"
                        text: "exports/ejemplo_importacion.csv"
                    }

                    HubButton {
                        id: previewBtn
                        text: "Analizar y Previsualizar"
                        variant: "primary"
                        anchors.bottom: csvPathInput.bottom
                        onClicked: {
                            var res = appController.previewCsv(csvPathInput.text);
                            if (res.success) {
                                root.previewData = res.data;
                            }
                        }
                    }
                }
            }
        }

        // ── Paso 2: Vista Previa y Columnas Detectadas ─────────────────────────
        HubCard {
            visible: root.previewData !== null
            width: parent.width - 48
            implicitHeight: 220

            Column {
                anchors.fill: parent
                spacing: 12

                Item {
                    width: parent.width
                    height: 18

                    Text {
                        anchors.left: parent.left
                        anchors.verticalCenter: parent.verticalCenter
                        text: "PASO 2: VISTA PREVIA (" + (root.previewData ? root.previewData.total_rows + " filas encontradas" : "") + ")"
                        font.pixelSize: 11
                        font.weight: Font.Bold
                        color: Theme.accentSuccess
                    }

                    Text {
                        anchors.right: parent.right
                        anchors.verticalCenter: parent.verticalCenter
                        text: "Codificación detectada: " + (root.previewData ? root.previewData.encoding : "")
                        font.pixelSize: 11
                        color: Theme.textMuted
                    }
                }

                Text {
                    text: "Columnas detectadas en el archivo: " + (root.previewData ? root.previewData.headers.join(", ") : "")
                    font.pixelSize: 12
                    font.family: Theme.fontFamily
                    color: Theme.textSecondary
                }

                // Muestra de primeras filas
                Rectangle {
                    width: parent.width
                    height: 90
                    radius: Theme.radiusSm
                    color: Theme.bgInput
                    border.color: Theme.borderSubtle

                    Column {
                        anchors.fill: parent
                        anchors.margins: 10
                        spacing: 4

                        Repeater {
                            model: root.previewData ? root.previewData.sample_rows : []
                            Text {
                                text: "Fila " + (index + 1) + ": " + modelData.join(" | ")
                                font.pixelSize: 11
                                font.family: "Consolas, monospace"
                                color: Theme.textPrimary
                                elide: Text.ElideRight
                                width: parent.width
                            }
                        }
                    }
                }

                // Botón Ejecutar Importación
                Row {
                    anchors.right: parent.right
                    spacing: 12

                    HubButton {
                        text: "Confirmar e Importar Contactos"
                        variant: "success"
                        onClicked: {
                            // Mapeo estándar por nombres de columnas
                            var mapping = {
                                "id": "ID",
                                "nombre": "Nombre Completo",
                                "telefono": "Teléfono",
                                "correo": "Correo Electrónico",
                                "ciudad": "Ciudad"
                            };
                            var res = appController.executeCsvImport(csvPathInput.text, mapping);
                            if (res.success) {
                                root.importSummary = res.summary;
                            }
                        }
                    }
                }
            }
        }

        // ── Paso 3: Resumen de Resultados ────────────────────────────────────
        HubCard {
            visible: root.importSummary !== null
            width: parent.width - 48
            implicitHeight: 140

            Column {
                anchors.fill: parent
                spacing: 10

                Text {
                    text: "RESUMEN DE RESULTADOS DE LA IMPORTACIÓN"
                    font.pixelSize: 11
                    font.weight: Font.Bold
                    color: Theme.accentPrimary
                }

                Row {
                    spacing: 16
                    HubBadge {
                        text: "Importados con éxito: " + (root.importSummary ? root.importSummary.imported : 0)
                        status: "ok"
                    }
                    HubBadge {
                        text: "Duplicados omitidos: " + (root.importSummary ? root.importSummary.skipped_duplicates : 0)
                        status: "warning"
                    }
                    HubBadge {
                        text: "Errores de validación: " + (root.importSummary ? root.importSummary.validation_errors : 0)
                        status: "error"
                    }
                }

                Text {
                    visible: root.importSummary && root.importSummary.errors_sample && root.importSummary.errors_sample.length > 0
                    text: "Detalles de errores: " + (root.importSummary ? root.importSummary.errors_sample.join(" | ") : "")
                    font.pixelSize: 11
                    color: Theme.textMuted
                    elide: Text.ElideRight
                    width: parent.width
                }
            }
        }
    }
}
