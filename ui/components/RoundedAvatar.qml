import QtQuick 2.15
import Qt5Compat.GraphicalEffects 1.15
import "../theme"

Item {
    id: root

    property string initials: "CH"
    property string source: ""
    property int radius: width / 2
    property color borderColor: Theme.accentPrimary
    property int borderWidth: 2

    implicitWidth: 40
    implicitHeight: 40

    Rectangle {
        id: bgCircle
        anchors.fill: parent
        radius: root.radius
        color: Theme.bgElevated
        border.color: root.borderColor
        border.width: root.borderWidth

        Text {
            anchors.centerIn: parent
            text: root.initials
            font.pixelSize: root.height * 0.38
            font.weight: Font.Bold
            font.family: Theme.fontFamily
            color: Theme.textPrimary
            visible: root.source === ""
        }
    }

    Image {
        id: rawImage
        anchors.fill: parent
        source: root.source
        fillMode: Image.PreserveAspectCrop
        visible: false
    }

    Rectangle {
        id: maskRect
        anchors.fill: parent
        radius: root.radius
        visible: false
    }

    OpacityMask {
        anchors.fill: parent
        source: rawImage
        maskSource: maskRect
        visible: root.source !== ""
    }
}

