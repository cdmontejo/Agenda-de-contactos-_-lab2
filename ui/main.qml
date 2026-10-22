import QtQuick 2.15
import QtQuick.Controls 2.15
import QtQuick.Layouts 1.15
import "theme"
import "components"
import "views"

ApplicationWindow {
    id: window

    visible: true
    width: 1280
    height: 760
    minimumWidth: 1040
    minimumHeight: 660
    title: "ContactHub Enterprise v2.0 — Gestión de Contactos con Acceso Aleatorio O(1)"
    color: Theme.bgBase

    property string activeView: "dashboard"

    // Sincronizar tema con AppController al arrancar
    Component.onCompleted: {
        Theme.activeTheme = appController.currentTheme;
    }

    // Conectar notificaciones Toast de Python
    Connections {
        target: appController
        function onToastRequested(msg, variant) {
            toast.show(msg, variant);
        }
        function onThemeChanged(newTheme) {
            Theme.activeTheme = newTheme;
        }
    }

    Row {
        anchors.fill: parent

        // ── Sidebar de Navegación Lateral Flotante ───────────────────────────
        Rectangle {
            id: sidebar
            width: 250
            height: parent.height
            color: Theme.bgSidebar
            border.color: Theme.borderSubtle
            border.width: 1

            Column {
                anchors.fill: parent
                anchors.margins: 16
                spacing: 14

                // Cabecera del Sidebar con Logo y Título
                Row {
                    spacing: 12
                    anchors.horizontalCenter: parent.horizontalCenter
                    width: parent.width

                    RoundedAvatar {
                        width: 40
                        height: 40
                        initials: "CH"
                        borderColor: Theme.accentPrimary
                        borderWidth: 2
                        anchors.verticalCenter: parent.verticalCenter
                    }

                    Column {
                        anchors.verticalCenter: parent.verticalCenter
                        spacing: 1

                        Text {
                            text: "ContactHub"
                            font.pixelSize: 16
                            font.weight: Font.Bold
                            font.family: Theme.fontFamily
                            color: Theme.textPrimary
                        }

                        Text {
                            text: "Enterprise Edition v2.0"
                            font.pixelSize: 11
                            font.family: Theme.fontFamily
                            color: Theme.accentPrimary
                        }
                    }
                }

                Rectangle {
                    width: parent.width
                    height: 1
                    color: Theme.borderSubtle
                }

                // Elementos del Menú de Navegación
                Column {
                    width: parent.width
                    spacing: 4

                    Repeater {
                        model: [
                            { id: "dashboard", label: "Dashboard Ejecutivo", icon: "📊" },
                            { id: "contacts",  label: "Directorio de Contactos", icon: "👥" },
                            { id: "integrity", label: "Integridad SHA-256", icon: "🛡️" },
                            { id: "backups",   label: "Respaldos Time Machine", icon: "📦" },
                            { id: "export",    label: "Exportar Reportes", icon: "📑" },
                            { id: "import",    label: "Importar desde CSV", icon: "📥" },
                            { id: "tools",     label: "Telemetría y Sistema", icon: "⚡" },
                            { id: "settings",  label: "Configuración", icon: "⚙️" },
                            { id: "help",      label: "Manual Técnico", icon: "❓" }
                        ]

                        Rectangle {
                            width: parent.width
                            height: 40
                            radius: Theme.radiusSm
                            color: window.activeView === modelData.id
                                   ? Qt.rgba(31/255, 168/255, 255/255, 0.15)
                                   : (navMouseArea.containsMouse ? Theme.bgElevated : "transparent")
                            border.color: window.activeView === modelData.id ? Theme.accentPrimary : "transparent"
                            border.width: 1

                            Row {
                                anchors.fill: parent
                                anchors.leftMargin: 12
                                anchors.rightMargin: 12
                                spacing: 10

                                Text {
                                    text: modelData.icon
                                    font.pixelSize: 14
                                    anchors.verticalCenter: parent.verticalCenter
                                }

                                Text {
                                    text: modelData.label
                                    font.pixelSize: 12
                                    font.weight: window.activeView === modelData.id ? Font.Bold : Font.Normal
                                    font.family: Theme.fontFamily
                                    color: window.activeView === modelData.id ? Theme.accentPrimary : Theme.textPrimary
                                    anchors.verticalCenter: parent.verticalCenter
                                }
                            }

                            MouseArea {
                                id: navMouseArea
                                anchors.fill: parent
                                hoverEnabled: true
                                cursorShape: Qt.PointingHandCursor
                                onClicked: window.activeView = modelData.id
                            }
                        }
                    }
                }

                Item { width: 1; height: 16 }

                // Píldora de Estado del Sello Criptográfico en Pie del Sidebar
                Rectangle {
                    width: parent.width
                    height: 60
                    radius: Theme.radiusSm
                    color: Theme.bgElevated
                    border.color: appController.isIntegrityValid ? Qt.rgba(16/255, 185/255, 129/255, 0.3) : Qt.rgba(239/255, 68/255, 68/255, 0.4)
                    border.width: 1

                    Column {
                        anchors.centerIn: parent
                        spacing: 4

                        Row {
                            spacing: 6
                            anchors.horizontalCenter: parent.horizontalCenter

                            Rectangle {
                                width: 8
                                height: 8
                                radius: 4
                                color: appController.isIntegrityValid ? Theme.accentSuccess : Theme.accentDanger
                                anchors.verticalCenter: parent.verticalCenter
                            }

                            Text {
                                text: appController.isIntegrityValid ? "Sello SHA-256 Válido" : "Sello Roto / Corrupto"
                                font.pixelSize: 11
                                font.weight: Font.Bold
                                font.family: Theme.fontFamily
                                color: appController.isIntegrityValid ? Theme.accentSuccess : Theme.accentDanger
                            }
                        }

                        Text {
                            text: appController.totalActiveContacts + " Contactos Activos en RAM"
                            font.pixelSize: 10
                            font.family: Theme.fontFamily
                            color: Theme.textMuted
                            anchors.horizontalCenter: parent.horizontalCenter
                        }
                    }
                }
            }
        }

        // ── Contenedor Principal de Contenido ────────────────────────────────
        Item {
            width: parent.width - sidebar.width
            height: parent.height

            Column {
                anchors.fill: parent

                // Barra Superior Contextual
                Rectangle {
                    width: parent.width
                    height: 54
                    color: Theme.bgSurface
                    border.color: Theme.borderSubtle
                    border.width: 1

                    Item {
                        anchors.fill: parent
                        anchors.leftMargin: 24
                        anchors.rightMargin: 24

                        Text {
                            anchors.left: parent.left
                            anchors.verticalCenter: parent.verticalCenter
                            text: {
                                switch (window.activeView) {
                                    case "dashboard": return "Dashboard Ejecutivo";
                                    case "contacts":  return "Directorio de Contactos — Acceso Aleatorio O(1)";
                                    case "integrity": return "Centro de Integridad Criptográfica SHA-256";
                                    case "backups":   return "Time Machine — Catálogo Histórico de Respaldos";
                                    case "export":    return "Centro de Exportación y Reportes PDF";
                                    case "import":    return "Importación Inteligente desde CSV";
                                    case "tools":     return "Herramientas del Sistema y Telemetría";
                                    case "settings":  return "Configuración y Preferencias";
                                    case "help":      return "Manual Técnico del Laboratorio";
                                    default:          return "ContactHub Enterprise";
                                }
                            }
                            font.pixelSize: 15
                            font.weight: Font.Bold
                            font.family: Theme.fontFamily
                            color: Theme.textPrimary
                        }

                        Row {
                            anchors.right: parent.right
                            anchors.verticalCenter: parent.verticalCenter
                            spacing: 10

                            // Conmutador rápido de tema
                            HubButton {
                                text: Theme.activeTheme === "dark" ? "☀️ Claro" : "🌙 Oscuro"
                                variant: "ghost"
                                implicitHeight: 34
                                onClicked: {
                                    var next = Theme.activeTheme === "dark" ? "light" : "dark";
                                    appController.setTheme(next);
                                }
                            }

                            // Botón Nuevo Contacto Rápido
                            HubButton {
                                text: "＋ Nuevo Contacto"
                                variant: "primary"
                                implicitHeight: 34
                                onClicked: contactFormModal.openNew()
                            }
                        }
                    }
                }

                // Área Central de Vistas Modulares
                Item {
                    width: parent.width
                    height: parent.height - 54

                    Loader {
                        id: viewLoader
                        anchors.fill: parent
                        sourceComponent: {
                            switch (window.activeView) {
                                case "dashboard": return dashboardComponent;
                                case "contacts":  return contactsComponent;
                                case "integrity": return integrityComponent;
                                case "backups":   return backupsComponent;
                                case "export":    return exportComponent;
                                case "import":    return importComponent;
                                case "tools":     return toolsComponent;
                                case "settings":  return settingsComponent;
                                case "help":      return helpComponent;
                                default:          return dashboardComponent;
                            }
                        }
                    }
                }
            }
        }
    }

    // ── Definición de Componentes de Vistas ──────────────────────────────────
    Component {
        id: dashboardComponent
        DashboardView {
            onNavigateTo: function(viewName) { window.activeView = viewName; }
            onOpenNewContactModal: function() { contactFormModal.openNew(); }
        }
    }

    Component {
        id: contactsComponent
        ContactsView {
            onOpenNewModal: function() { contactFormModal.openNew(); }
            onOpenEditModal: function(c) { contactFormModal.openEdit(c); }
            onOpenInspectModal: function(c, insp) {
                contactDetailModal.contactData = c;
                contactDetailModal.inspectionData = insp;
                contactDetailModal.open();
            }
        }
    }

    Component { id: integrityComponent; IntegrityView {} }
    Component { id: backupsComponent; BackupsView {} }
    Component { id: exportComponent; ExportView {} }
    Component { id: importComponent; ImportView {} }
    Component { id: toolsComponent; ToolsView {} }
    Component { id: settingsComponent; SettingsView {} }
    Component { id: helpComponent; HelpView {} }

    // ── Modales Globales ─────────────────────────────────────────────────────
    ContactDetailModal {
        id: contactDetailModal
    }

    ContactFormModal {
        id: contactFormModal

        function openNew() {
            root.isEdit = false;
            root.initialId = "";
            root.initialNombre = "";
            root.initialTelefono = "";
            root.initialCorreo = "";
            root.initialCiudad = "";
            open();
        }

        function openEdit(c) {
            root.isEdit = true;
            root.initialId = c.id.toString();
            root.initialNombre = c.nombre;
            root.initialTelefono = c.telefono;
            root.initialCorreo = c.correo;
            root.initialCiudad = c.ciudad;
            open();
        }

        onSaved: {
            appController.loadContacts();
        }
    }

    // ── Notificaciones Toast Flotantes ───────────────────────────────────────
    HubToast {
        id: toast
        anchors.bottom: parent.bottom
        anchors.right: parent.right
        anchors.margins: 24
    }
}
