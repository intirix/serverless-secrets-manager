import QtQuick 2.0

Rectangle {
    id: box
    property int vpadding: 5
    height: input.implicitHeight + vpadding * 2
    color: "#FFFFFF"
    border.color: "#3F51B5"
    border.width: 1
    radius: height * 1 / 3
    property alias text: input.text
    property alias inputMethodHints: input.inputMethodHints
    property alias echoMode: input.echoMode
    anchors {
        left: parent.left
        right: parent.right
        topMargin: 10
        rightMargin: 20
        leftMargin: 20
    }
    TextInput {
        id: input
        anchors {
            fill: parent
            leftMargin: parent.height * 1 / 3
            topMargin: parent.vpadding
            bottomMargin: parent.vpadding
        }

        height: parent.height
        width: parent.width - parent.radius * 2
        text: "Enter value"
        horizontalAlignment: TextInput.AlignLeft | TextInput.AlignHCenter
    }
}
