import QtQuick 2.15
import "../theme"

Rectangle {
    id: root

    property string title: "Total Contactos"
    property string value: "0"
    property string subtitle: ""
    property string icon: "👤"
    property color accentColor: Theme.accentPrimary

    implicitWidth: 220
    implicitHeight: 104
    radius: Theme.radiusMd
    color: Theme.bgCard
    border.color: Theme.borderSubtle
    border.width: 1

    Rectangle {
        width: 4
        height: parent.height - 24
        radius: 2
        color: root.accentColor
        anchors.left: parent.left
        anchors.leftMargin: 8
        anchors.verticalCenter: parent.verticalCenter
    }

    Item {
        anchors.fill: parent
        anchors.leftMargin: 20
        anchors.rightMargin: 16
        anchors.topMargin: 14
        anchors.bottomMargin: 14

        Item {
            width: parent.width
            height: 20
            anchors.top: parent.top

            Text {
                anchors.left: parent.left
                anchors.verticalCenter: parent.verticalCenter
                text: root.title.toUpperCase()
                font.pixelSize: 11
                font.weight: Font.Bold
                font.family: Theme.fontFamily
                color: Theme.textSecondary
                elide: Text.ElideRight
                width: parent.width - iconText.width - 4
            }

            Text {
                id: iconText
                anchors.right: parent.right
                anchors.verticalCenter: parent.verticalCenter
                text: root.icon
                font.pixelSize: 16
            }
        }

        Text {
            text: root.value
            font.pixelSize: 26
            font.weight: Font.Bold
            font.family: Theme.fontFamily
            color: Theme.textPrimary
            anchors.bottom: subtitleText.visible ? subtitleText.top : parent.bottom
            anchors.bottomMargin: subtitleText.visible ? 2 : 0
        }

        Text {
            id: subtitleText
            visible: root.subtitle !== ""
            text: root.subtitle
            font.pixelSize: 11
            font.family: Theme.fontFamily
            color: Theme.textMuted
            anchors.bottom: parent.bottom
            elide: Text.ElideRight
            width: parent.width
        }
    }
}
