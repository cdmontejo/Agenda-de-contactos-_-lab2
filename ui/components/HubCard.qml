import QtQuick 2.15
import "../theme"

Rectangle {
    id: root

    default property alias content: container.data
    property int contentPadding: 16
    property bool hoverElevate: false
    property bool interactive: false

    signal clicked()

    implicitWidth: 320
    implicitHeight: 200
    radius: Theme.radiusMd
    color: Theme.bgCard
    border.color: Theme.borderSubtle
    border.width: 1

    Behavior on color { ColorAnimation { duration: Theme.animFast } }
    Behavior on border.color { ColorAnimation { duration: Theme.animFast } }

    MouseArea {
        id: mouseArea
        anchors.fill: parent
        enabled: root.interactive
        hoverEnabled: root.hoverElevate || root.interactive
        cursorShape: root.interactive ? Qt.PointingHandCursor : Qt.ArrowCursor
        onClicked: root.clicked()
    }

    Item {
        id: container
        anchors.fill: parent
        anchors.margins: root.contentPadding
    }
}
