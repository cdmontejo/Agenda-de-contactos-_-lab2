import QtQuick 2.15
import QtQuick.Controls 2.15
import "../theme"

Dialog {
    id: root

    property string titleText: "Confirmación"
    property string messageText: "¿Desea continuar con esta acción?"
    property string confirmText: "Confirmar"
    property string cancelText: "Cancelar"
    property string confirmVariant: "primary" // "primary", "danger"

    signal confirmed()
    signal cancelled()

    modal: true
    dim: true
    anchors.centerIn: parent
    implicitWidth: 400
    implicitHeight: 220
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

            Text {
                text: root.titleText
                font.pixelSize: 16
                font.weight: Font.Bold
                font.family: Theme.fontFamily
                color: Theme.textPrimary
            }

            Text {
                width: parent.width
                text: root.messageText
                font.pixelSize: 13
                font.family: Theme.fontFamily
                color: Theme.textSecondary
                wrapMode: Text.Wrap
            }

            Item { width: 1; height: 16 }

            Row {
                anchors.right: parent.right
                spacing: 10

                HubButton {
                    text: root.cancelText
                    variant: "secondary"
                    onClicked: {
                        root.cancelled();
                        root.close();
                    }
                }

                HubButton {
                    text: root.confirmText
                    variant: root.confirmVariant
                    onClicked: {
                        root.confirmed();
                        root.close();
                    }
                }
            }
        }
    }
}
