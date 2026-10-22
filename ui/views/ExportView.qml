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
        spacing: 24
        padding: 24

        Column {
            spacing: 4
            Text {
                text: "Centro de Exportación y Reportes Ejecutivos"
                font.pixelSize: 20
                font.weight: Font.Bold
                font.family: Theme.fontFamily
                color: Theme.textPrimary
            }
            Text {
                text: "Generación de documentos normalizados para integración con hojas de cálculo, APIs y reportes ejecutivos"
                font.pixelSize: 13
                font.family: Theme.fontFamily
                color: Theme.textSecondary
            }
        }

        // ── Tarjetas de Opciones de Exportación ───────────────────────────────
        Row {
            width: parent.width - 48
            spacing: 16

            // Tarjeta PDF
            HubCard {
                width: (parent.width - 32) / 3
                implicitHeight: 260

                Column {
                    anchors.fill: parent
                    spacing: 14

                    Rectangle {
                        width: 44
                        height: 44
                        radius: 10
                        color: Qt.rgba(239/255, 68/255, 68/255, 0.15)
                        Text { anchors.centerIn: parent; text: "📑"; font.pixelSize: 20 }
                    }

                    Text {
                        text: "Reporte Ejecutivo PDF"
                        font.pixelSize: 16
                        font.weight: Font.Bold
                        font.family: Theme.fontFamily
                        color: Theme.textPrimary
                    }

                    Text {
                        width: parent.width
                        text: "Genera un documento PDF corporativo con fpdf2. Incluye cabecera oficial, resumen estadístico de almacenamiento, tablas paginadas y verificación de sello SHA-256."
                        font.pixelSize: 12
                        font.family: Theme.fontFamily
                        color: Theme.textSecondary
                        wrapMode: Text.Wrap
                    }

                    Item { width: 1; height: 8 }

                    HubButton {
                        text: "Exportar a PDF"
                        variant: "primary"
                        width: parent.width
                        onClicked: appController.exportToPdf()
                    }
                }
            }

            // Tarjeta CSV
            HubCard {
                width: (parent.width - 32) / 3
                implicitHeight: 260

                Column {
                    anchors.fill: parent
                    spacing: 14

                    Rectangle {
                        width: 44
                        height: 44
                        radius: 10
                        color: Qt.rgba(16/255, 185/255, 129/255, 0.15)
                        Text { anchors.centerIn: parent; text: "📊"; font.pixelSize: 20 }
                    }

                    Text {
                        text: "Hoja de Cálculo CSV"
                        font.pixelSize: 16
                        font.weight: Font.Bold
                        font.family: Theme.fontFamily
                        color: Theme.textPrimary
                    }

                    Text {
                        width: parent.width
                        text: "Exporta todos los contactos con codificación UTF-8 BOM (Byte Order Mark), garantizando compatibilidad nativa con Microsoft Excel sin distorsión de tildes o eñes."
                        font.pixelSize: 12
                        font.family: Theme.fontFamily
                        color: Theme.textSecondary
                        wrapMode: Text.Wrap
                    }

                    Item { width: 1; height: 8 }

                    HubButton {
                        text: "Exportar a CSV"
                        variant: "success"
                        width: parent.width
                        onClicked: appController.exportToCsv()
                    }
                }
            }

            // Tarjeta JSON
            HubCard {
                width: (parent.width - 32) / 3
                implicitHeight: 260

                Column {
                    anchors.fill: parent
                    spacing: 14

                    Rectangle {
                        width: 44
                        height: 44
                        radius: 10
                        color: Qt.rgba(31/255, 168/255, 255/255, 0.15)
                        Text { anchors.centerIn: parent; text: "⚡"; font.pixelSize: 20 }
                    }

                    Text {
                        text: "Estructura JSON"
                        font.pixelSize: 16
                        font.weight: Font.Bold
                        font.family: Theme.fontFamily
                        color: Theme.textPrimary
                    }

                    Text {
                        width: parent.width
                        text: "Documento estructurado JSON con metadatos del sistema, hash de integridad del archivo fuente y colección completa de contactos para interoperabilidad."
                        font.pixelSize: 12
                        font.family: Theme.fontFamily
                        color: Theme.textSecondary
                        wrapMode: Text.Wrap
                    }

                    Item { width: 1; height: 8 }

                    HubButton {
                        text: "Exportar a JSON"
                        variant: "secondary"
                        width: parent.width
                        onClicked: appController.exportToJson()
                    }
                }
            }
        }
    }
}
