import QtQuick 2.15
import QtQuick.Controls 2.15
import "../theme"

Button {
    id: control

    // Variantes: "primary", "secondary", "success", "danger", "ghost", "warning"
    property string variant: "primary"
    property string iconText: ""
    property bool busy: false

    implicitWidth: Math.max(100, contentRow.implicitWidth + leftPadding + rightPadding)
    implicitHeight: 38
    leftPadding: 16
    rightPadding: 16
    topPadding: 0
    bottomPadding: 0
    hoverEnabled: true
    enabled: !busy

    font.pixelSize: 13
    font.weight: Font.DemiBold
    font.family: Theme.fontFamily

    readonly property color fillIdle: {
        switch (variant) {
            case "primary":   return Theme.accentPrimary
            case "success":   return Theme.accentSuccess
            case "danger":    return Theme.accentDanger
            case "warning":   return Theme.accentWarning
            case "secondary": return Theme.bgElevated
            case "ghost":     return "transparent"
            default:          return Theme.accentPrimary
        }
    }

    readonly property color fillHover: {
        switch (variant) {
            case "primary":   return Theme.accentPrimaryHover
            case "success":   return Qt.lighter(Theme.accentSuccess, 1.15)
            case "danger":    return Qt.lighter(Theme.accentDanger, 1.15)
            case "warning":   return Qt.lighter(Theme.accentWarning, 1.15)
            case "secondary": return Qt.lighter(Theme.bgElevated, 1.15)
            case "ghost":     return Theme.bgElevated
            default:          return Theme.accentPrimaryHover
        }
    }

    readonly property color fillPressed: {
        switch (variant) {
            case "primary":   return Theme.accentPrimaryPressed
            case "success":   return Qt.darker(Theme.accentSuccess, 1.2)
            case "danger":    return Qt.darker(Theme.accentDanger, 1.2)
            case "warning":   return Qt.darker(Theme.accentWarning, 1.2)
            case "secondary": return Qt.darker(Theme.bgElevated, 1.1)
            case "ghost":     return Qt.darker(Theme.bgElevated, 1.2)
            default:          return Theme.accentPrimaryPressed
        }
    }

    readonly property color textColor: {
        if (!control.enabled) return Theme.textMuted
        switch (variant) {
            case "ghost":     return Theme.textPrimary
            case "secondary": return Theme.textPrimary
            default:          return Theme.textOnAccent
        }
    }

    background: Rectangle {
        implicitWidth: control.implicitWidth
        implicitHeight: control.implicitHeight
        radius: Theme.radiusSm
        color: control.down ? control.fillPressed : (control.hovered ? control.fillHover : control.fillIdle)
        border.color: variant === "ghost" ? "transparent" : (variant === "secondary" ? Theme.borderSubtle : "transparent")
        border.width: 1

        Behavior on color {
            ColorAnimation { duration: Theme.animFast }
        }
    }

    contentItem: Row {
        id: contentRow
        spacing: 8
        anchors.centerIn: parent

        Text {
            visible: control.iconText !== "" && !control.busy
            text: control.iconText
            font.pixelSize: 14
            color: control.textColor
            anchors.verticalCenter: parent.verticalCenter
        }

        // Spinner para estado ocupado
        BusyIndicator {
            visible: control.busy
            running: control.busy
            implicitWidth: 16
            implicitHeight: 16
            anchors.verticalCenter: parent.verticalCenter
        }

        Text {
            text: control.text
            font: control.font
            color: control.textColor
            horizontalAlignment: Text.AlignHCenter
            verticalAlignment: Text.AlignVCenter
            anchors.verticalCenter: parent.verticalCenter
        }
    }
}
