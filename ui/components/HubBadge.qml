import QtQuick 2.15
import "../theme"

Rectangle {
    id: root

    property string text: "Activo"
    property string status: "ok" // "ok", "error", "warning", "info", "neutral"

    readonly property color badgeColor: {
        switch (status) {
            case "ok":
            case "A":
            case "activo":     return Theme.accentSuccess
            case "error":
            case "D":
            case "eliminado":  return Theme.accentDanger
            case "warning":    return Theme.accentWarning
            case "info":       return Theme.accentInfo
            default:           return Theme.textMuted
        }
    }

    implicitWidth: label.implicitWidth + 14
    implicitHeight: 22
    radius: 11
    color: Qt.rgba(badgeColor.r, badgeColor.g, badgeColor.b, 0.15)
    border.color: Qt.rgba(badgeColor.r, badgeColor.g, badgeColor.b, 0.35)
    border.width: 1

    Row {
        anchors.centerIn: parent
        spacing: 5

        Rectangle {
            width: 6
            height: 6
            radius: 3
            color: root.badgeColor
            anchors.verticalCenter: parent.verticalCenter
        }

        Text {
            id: label
            text: root.text
            font.pixelSize: 11
            font.weight: Font.DemiBold
            font.family: Theme.fontFamily
            color: root.badgeColor
            anchors.verticalCenter: parent.verticalCenter
        }
    }
}

