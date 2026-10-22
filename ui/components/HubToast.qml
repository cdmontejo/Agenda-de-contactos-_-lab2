import QtQuick 2.15
import "../theme"

Rectangle {
    id: root

    property string message: ""
    property string variant: "info" // "success", "danger", "warning", "info"
    property int duration: 4000

    signal closed()

    readonly property color toastColor: {
        switch (variant) {
            case "success": return Theme.accentSuccess
            case "danger":  return Theme.accentDanger
            case "warning": return Theme.accentWarning
            default:        return Theme.accentInfo
        }
    }

    readonly property string iconSymbol: {
        switch (variant) {
            case "success": return "✓"
            case "danger":  return "✕"
            case "warning": return "⚠"
            default:        return "ℹ"
        }
    }

    implicitWidth: Math.min(420, Math.max(260, textContent.implicitWidth + 72))
    implicitHeight: Math.max(48, textContent.implicitHeight + 24)
    radius: Theme.radiusSm
    color: Theme.bgElevated
    border.color: root.toastColor
    border.width: 1.5

    // Efecto de entrada y salida
    opacity: 0
    y: 20

    Behavior on opacity { NumberAnimation { duration: Theme.animFast } }
    Behavior on y { NumberAnimation { duration: Theme.animFast; easing.type: Easing.OutQuad } }

    Timer {
        id: autoCloseTimer
        interval: root.duration
        running: false
        repeat: false
        onTriggered: root.dismiss()
    }

    function show(msg, v) {
        root.message = msg;
        root.variant = v || "info";
        root.opacity = 1;
        root.y = 0;
        autoCloseTimer.restart();
    }

    function dismiss() {
        root.opacity = 0;
        root.y = 20;
        root.closed();
    }

    Row {
        anchors.fill: parent
        anchors.margins: 12
        spacing: 12

        Rectangle {
            width: 24
            height: 24
            radius: 12
            color: Qt.rgba(root.toastColor.r, root.toastColor.g, root.toastColor.b, 0.2)
            anchors.verticalCenter: parent.verticalCenter

            Text {
                text: root.iconSymbol
                font.pixelSize: 13
                font.weight: Font.Bold
                color: root.toastColor
                anchors.centerIn: parent
            }
        }

        Text {
            id: textContent
            text: root.message
            font.pixelSize: 12
            font.family: Theme.fontFamily
            color: Theme.textPrimary
            wrapMode: Text.Wrap
            width: root.width - 76
            anchors.verticalCenter: parent.verticalCenter
        }

        Text {
            text: "×"
            font.pixelSize: 18
            color: Theme.textMuted
            anchors.verticalCenter: parent.verticalCenter

            MouseArea {
                anchors.fill: parent
                cursorShape: Qt.PointingHandCursor
                onClicked: root.dismiss()
            }
        }
    }
}
