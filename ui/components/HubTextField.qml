import QtQuick 2.15
import QtQuick.Controls 2.15
import "../theme"

Item {
    id: root

    property alias text: input.text
    property string placeholderText: ""
    property alias echoMode: input.echoMode
    property alias readOnly: input.readOnly
    property alias validator: input.validator
    property alias inputMethodHints: input.inputMethodHints

    function forceActiveFocus() {
        input.forceActiveFocus();
    }

    property string label: ""
    property string helperText: ""
    property string errorMessage: ""
    property int maxBytes: 0
    property bool hasError: errorMessage !== ""

    // Cálculo aproximado de bytes consumidos en UTF-8
    readonly property int currentBytes: {
        var str = input.text;
        var s = 0;
        for (var i = 0; i < str.length; i++) {
            var code = str.charCodeAt(i);
            if (code <= 0x7f) s += 1;
            else if (code <= 0x7ff) s += 2;
            else if (code <= 0xffff) s += 3;
            else s += 4;
        }
        return s;
    }

    implicitWidth: 280
    implicitHeight: (label !== "" ? 22 : 0) + 40 + (helperText !== "" || errorMessage !== "" || maxBytes > 0 ? 18 : 0)

    Column {
        anchors.fill: parent
        spacing: 4

        // Etiqueta superior
        Item {
            width: parent.width
            height: labelText.implicitHeight
            visible: root.label !== ""

            Text {
                id: labelText
                anchors.left: parent.left
                text: root.label
                font.pixelSize: 12
                font.weight: Font.Medium
                font.family: Theme.fontFamily
                color: root.hasError ? Theme.accentDanger : Theme.textSecondary
            }

            Text {
                visible: root.maxBytes > 0
                anchors.right: parent.right
                text: root.currentBytes + " / " + root.maxBytes + " B"
                font.pixelSize: 11
                font.family: Theme.fontFamily
                color: root.currentBytes > root.maxBytes ? Theme.accentDanger : Theme.textMuted
            }
        }

        // Campo de entrada
        Rectangle {
            width: parent.width
            height: 40
            radius: Theme.radiusSm
            color: root.readOnly ? Theme.bgElevated : Theme.bgInput
            border.color: root.hasError ? Theme.accentDanger : (input.activeFocus ? Theme.borderFocus : Theme.borderSubtle)
            border.width: input.activeFocus || root.hasError ? 1.5 : 1

            Behavior on border.color {
                ColorAnimation { duration: Theme.animFast }
            }

            TextInput {
                id: input
                anchors.fill: parent
                anchors.leftMargin: 12
                anchors.rightMargin: 12
                verticalAlignment: TextInput.AlignVCenter
                font.pixelSize: 13
                font.family: Theme.fontFamily
                color: Theme.textPrimary
                selectionColor: Theme.accentPrimary
                selectedTextColor: Theme.textOnAccent
                clip: true

                Text {
                    anchors.fill: parent
                    verticalAlignment: Text.AlignVCenter
                    text: root.placeholderText
                    font: input.font
                    color: Theme.textMuted
                    visible: !input.text && !input.activeFocus
                }
            }
        }

        // Mensaje de ayuda o error
        Text {
            width: parent.width
            visible: root.hasError || root.helperText !== ""
            text: root.hasError ? root.errorMessage : root.helperText
            font.pixelSize: 11
            font.family: Theme.fontFamily
            color: root.hasError ? Theme.accentDanger : Theme.textMuted
            elide: Text.ElideRight
        }
    }
}
