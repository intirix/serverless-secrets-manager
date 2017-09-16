import QtQuick 2.0


Rectangle {
    id: header
    color: "#3F51B5"
    anchors.top: parent.top
    anchors.left: parent.left
    anchors.right: parent.right
    anchors.margins: 10
    height: 40

    Text {
        color: "#FFFFFF"
        text: "Cloud Password Manager"
        font.pixelSize: 30
        anchors.verticalCenter: parent.verticalCenter
        anchors.left: parent.left
        anchors.leftMargin: 20
    }
}

