import QtQuick 2.15
import QtQuick.Controls 2.15
import QtQuick.Layouts 1.15
import "../theme"
import "../components"

Item {
    id: root

    signal openNewModal()
    signal openEditModal(var contact)
    signal openInspectModal(var contact, var inspection)

    property string currentStatusFilter: "activos"
    property string currentSearchField: "todos"

    Column {
        anchors.fill: parent
        anchors.margins: 24
        spacing: 16

        // ── Barra Superior de Herramientas y Filtros ──────────────────────────
        Item {
            width: parent.width
            height: 40

            Row {
                anchors.left: parent.left
                anchors.verticalCenter: parent.verticalCenter
                spacing: 12

                // Input de búsqueda rápida
                Rectangle {
                    width: 320
                    height: 40
                    radius: Theme.radiusSm
                    color: Theme.bgInput
                    border.color: searchInput.activeFocus ? Theme.borderFocus : Theme.borderSubtle
                    border.width: 1

                    Row {
                        anchors.fill: parent
                        anchors.margins: 10
                        spacing: 8

                        Text { text: "🔍"; font.pixelSize: 13; anchors.verticalCenter: parent.verticalCenter }

                        TextInput {
                            id: searchInput
                            anchors.verticalCenter: parent.verticalCenter
                            width: parent.width - 30
                            font.pixelSize: 13
                            font.family: Theme.fontFamily
                            color: Theme.textPrimary
                            selectByMouse: true
                            clip: true

                            Text {
                                anchors.fill: parent
                                text: "Buscar por nombre, ID, teléfono..."
                                font: parent.font
                                color: Theme.textMuted
                                visible: !searchInput.text && !searchInput.activeFocus
                            }

                            onTextChanged: {
                                appController.filterContacts(
                                    searchInput.text,
                                    root.currentSearchField,
                                    root.currentStatusFilter
                                );
                            }
                        }
                    }
                }

                // Filtro por Estado (Pestañas Activos / Eliminados / Todos)
                Row {
                    spacing: 4
                    anchors.verticalCenter: parent.verticalCenter

                    HubButton {
                        text: "Activos (" + appController.totalActiveContacts + ")"
                        variant: root.currentStatusFilter === "activos" ? "primary" : "ghost"
                        implicitHeight: 36
                        onClicked: {
                            root.currentStatusFilter = "activos";
                            appController.filterContacts(searchInput.text, root.currentSearchField, "activos");
                        }
                    }

                    HubButton {
                        text: "Eliminados (" + appController.totalDeletedContacts + ")"
                        variant: root.currentStatusFilter === "eliminados" ? "danger" : "ghost"
                        implicitHeight: 36
                        onClicked: {
                            root.currentStatusFilter = "eliminados";
                            appController.filterContacts(searchInput.text, root.currentSearchField, "eliminados");
                        }
                    }

                    HubButton {
                        text: "Todos (" + appController.totalPhysicalRecords + ")"
                        variant: root.currentStatusFilter === "todos" ? "secondary" : "ghost"
                        implicitHeight: 36
                        onClicked: {
                            root.currentStatusFilter = "todos";
                            appController.filterContacts(searchInput.text, root.currentSearchField, "todos");
                        }
                    }
                }
            }

            // Botón para crear nuevo contacto
            HubButton {
                anchors.right: parent.right
                anchors.verticalCenter: parent.verticalCenter
                text: "＋ Nuevo Contacto"
                variant: "primary"
                onClicked: root.openNewModal()
            }
        }

        // ── Cabecera de la Tabla ─────────────────────────────────────────────
        Rectangle {
            width: parent.width
            height: 40
            radius: Theme.radiusSm
            color: Theme.bgElevated
            border.color: Theme.borderSubtle

            Row {
                anchors.fill: parent
                anchors.leftMargin: 16
                anchors.rightMargin: 16
                spacing: 12

                Text { text: "ID"; width: 60; font.weight: Font.Bold; font.pixelSize: 11; color: Theme.textSecondary; anchors.verticalCenter: parent.verticalCenter }
                Text { text: "NOMBRE COMPLETO"; width: 220; font.weight: Font.Bold; font.pixelSize: 11; color: Theme.textSecondary; anchors.verticalCenter: parent.verticalCenter }
                Text { text: "TELÉFONO"; width: 130; font.weight: Font.Bold; font.pixelSize: 11; color: Theme.textSecondary; anchors.verticalCenter: parent.verticalCenter }
                Text { text: "CORREO ELECTRÓNICO"; width: 200; font.weight: Font.Bold; font.pixelSize: 11; color: Theme.textSecondary; anchors.verticalCenter: parent.verticalCenter }
                Text { text: "CIUDAD"; width: 130; font.weight: Font.Bold; font.pixelSize: 11; color: Theme.textSecondary; anchors.verticalCenter: parent.verticalCenter }
                Text { text: "OFFSET EN DISCO"; width: 140; font.weight: Font.Bold; font.pixelSize: 11; color: Theme.textSecondary; anchors.verticalCenter: parent.verticalCenter }
                Text { text: "ACCIONES"; width: 160; font.weight: Font.Bold; font.pixelSize: 11; color: Theme.textSecondary; anchors.verticalCenter: parent.verticalCenter; horizontalAlignment: Text.AlignRight }
            }
        }

        // ── Lista de Registros con Virtualización ─────────────────────────────
        ListView {
            id: contactsList
            width: parent.width
            height: parent.height - 120
            clip: true
            spacing: 6
            model: appController.contactModel

            delegate: Rectangle {
                width: contactsList.width
                height: 52
                radius: Theme.radiusSm
                color: model.estado === "A" ? Theme.bgCard : Qt.rgba(239/255, 68/255, 68/255, 0.08)
                border.color: Theme.borderSubtle
                border.width: 1

                Row {
                    anchors.fill: parent
                    anchors.leftMargin: 16
                    anchors.rightMargin: 16
                    spacing: 12

                    // ID
                    Text {
                        text: model.id
                        width: 60
                        font.pixelSize: 13
                        font.weight: Font.Bold
                        font.family: "Consolas, monospace"
                        color: Theme.accentPrimary
                        anchors.verticalCenter: parent.verticalCenter
                    }

                    // Nombre Completo
                    Text {
                        text: model.nombre
                        width: 220
                        font.pixelSize: 13
                        font.weight: Font.Medium
                        font.family: Theme.fontFamily
                        color: Theme.textPrimary
                        elide: Text.ElideRight
                        anchors.verticalCenter: parent.verticalCenter
                    }

                    // Teléfono
                    Text {
                        text: model.telefono
                        width: 130
                        font.pixelSize: 12
                        font.family: Theme.fontFamily
                        color: Theme.textSecondary
                        anchors.verticalCenter: parent.verticalCenter
                    }

                    // Correo Electrónico
                    Text {
                        text: model.correo
                        width: 200
                        font.pixelSize: 12
                        font.family: Theme.fontFamily
                        color: Theme.textSecondary
                        elide: Text.ElideRight
                        anchors.verticalCenter: parent.verticalCenter
                    }

                    // Ciudad
                    Text {
                        text: model.ciudad
                        width: 130
                        font.pixelSize: 12
                        font.family: Theme.fontFamily
                        color: Theme.textSecondary
                        elide: Text.ElideRight
                        anchors.verticalCenter: parent.verticalCenter
                    }

                    // Badge de Offset y Acceso Aleatorio
                    Row {
                        width: 140
                        spacing: 6
                        anchors.verticalCenter: parent.verticalCenter

                        HubBadge {
                            text: model.byteOffset + " B"
                            status: "info"
                        }

                        HubBadge {
                            text: model.estado === "A" ? "Activo" : "Eliminado"
                            status: model.estado === "A" ? "ok" : "error"
                        }
                    }

                    // Botones de Acción
                    Row {
                        width: 160
                        spacing: 6
                        anchors.verticalCenter: parent.verticalCenter
                        layoutDirection: Qt.RightToLeft

                        // Inspeccionar seek() y tell()
                        HubButton {
                            text: "🔍"
                            variant: "ghost"
                            implicitWidth: 34
                            implicitHeight: 32
                            onClicked: {
                                var res = appController.getContactInspection(model.id.toString());
                                if (res.success) {
                                    root.openInspectModal(model, res.data);
                                }
                            }
                        }

                        // Editar in-place (si está activo)
                        HubButton {
                            visible: model.estado === "A"
                            text: "✏️"
                            variant: "ghost"
                            implicitWidth: 34
                            implicitHeight: 32
                            onClicked: {
                                root.openEditModal({
                                    id: model.id,
                                    nombre: model.nombre,
                                    telefono: model.telefono,
                                    correo: model.correo,
                                    ciudad: model.ciudad
                                });
                            }
                        }

                        // Eliminar (si está activo)
                        HubButton {
                            visible: model.estado === "A"
                            text: "🗑️"
                            variant: "danger"
                            implicitWidth: 34
                            implicitHeight: 32
                            onClicked: {
                                deleteConfirmDialog.targetId = model.id.toString();
                                deleteConfirmDialog.targetName = model.nombre;
                                deleteConfirmDialog.open();
                            }
                        }

                        // Restaurar (si está eliminado 'D')
                        HubButton {
                            visible: model.estado === "D"
                            text: "♻️ Restaurar"
                            variant: "success"
                            implicitHeight: 32
                            onClicked: {
                                appController.restoreContact(model.id.toString());
                            }
                        }
                    }
                }
            }
        }
    }

    // Diálogo de confirmación para eliminación lógica
    HubDialog {
        id: deleteConfirmDialog
        property string targetId: ""
        property string targetName: ""

        titleText: "Eliminar Contacto"
        messageText: "¿Está seguro de eliminar a '" + targetName + "' (ID: " + targetId + ")? El registro se marcará lógicamente con el byte 'D' en disco in-place y podrá restaurarse en cualquier momento."
        confirmText: "Eliminar"
        confirmVariant: "danger"
        onConfirmed: {
            appController.deleteContact(targetId);
        }
    }
}
