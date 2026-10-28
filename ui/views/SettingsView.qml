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

        Column {
            spacing: 4
            Text {
                text: "Configuración y Preferencias del Sistema"
                font.pixelSize: 20
                font.weight: Font.Bold
                font.family: Theme.fontFamily
                color: Theme.textPrimary
            }
            Text {
                text: "Personalización del entorno visual, utilidades de laboratorio y detalles de versión"
                font.pixelSize: 13
                font.family: Theme.fontFamily
                color: Theme.textSecondary
            }
        }

        // ── Selector de Tema Visual ──────────────────────────────────────────
        HubCard {
            width: parent.width - 48
            implicitHeight: 120

            Column {
                anchors.fill: parent
                spacing: 12

                Text {
                    text: "TEMA VISUAL DE LA INTERFAZ"
                    font.pixelSize: 11
                    font.weight: Font.Bold
                    color: Theme.accentPrimary
                }

                Row {
                    spacing: 16

                    HubButton {
                        text: "🌙 Tema Oscuro (Dark Liquid Glass)"
                        variant: appController.currentTheme === "dark" ? "primary" : "secondary"
                        onClicked: {
                            appController.setTheme("dark");
                            Theme.activeTheme = "dark";
                        }
                    }

                    HubButton {
                        text: "☀️ Tema Claro (Clean Slate)"
                        variant: appController.currentTheme === "light" ? "primary" : "secondary"
                        onClicked: {
                            appController.setTheme("light");
                            Theme.activeTheme = "light";
                        }
                    }
                }
            }
        }

        // ── Generador de Datos de Demostración ────────────────────────────────
        HubCard {
            width: parent.width - 48
            implicitHeight: 130

            Column {
                anchors.fill: parent
                spacing: 12

                Text {
                    text: "GENERADOR DE DATOS DE LABORATORIO (SEED DATA)"
                    font.pixelSize: 11
                    font.weight: Font.Bold
                    color: Theme.accentSuccess
                }

                Text {
                    text: "Inserta registros ficticios realistas con nombres en español, tildes, eñes y diferentes ciudades guatemaltecas para probar el acceso aleatorio y las búsquedas."
                    font.pixelSize: 12
                    color: Theme.textSecondary
                }

                Row {
                    spacing: 12

                    HubButton {
                        text: "Insertar 10 Contactos Demo"
                        variant: "secondary"
                        onClicked: appController.seedDemoData(10)
                    }
                }
            }
        }

        // ── Acerca de ContactHub Enterprise ──────────────────────────────────
        HubCard {
            width: parent.width - 48
            implicitHeight: 140

            Column {
                anchors.fill: parent
                spacing: 8

                Text {
                    text: "ACERCA DE CONTACTHUB ENTERPRISE"
                    font.pixelSize: 11
                    font.weight: Font.Bold
                    color: Theme.accentPurple
                }

                Text {
                    text: "ContactHub Enterprise v2.0 — Edición Profesional para Laboratorio No. 2"
                    font.pixelSize: 13
                    font.weight: Font.Bold
                    color: Theme.textPrimary
                }

                Text {
                    text: "Facultad de Ingeniería en Informática y Sistemas — Universidad Rafael Landívar\nDesarrollado con PySide6 (Qt Quick/QML), persistencia binaria estricta de 256 bytes, índice primario JSON y verificación criptográfica SHA-256."
                    font.pixelSize: 12
                    color: Theme.textSecondary
                    wrapMode: Text.Wrap
                    width: parent.width
                }
            }
        }
    }
}

