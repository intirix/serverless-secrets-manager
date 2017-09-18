import QtQuick 2.0


Rectangle {
    id: header
    color: "#3F51B5"
    anchors.top: parent.top
    anchors.left: parent.left
    anchors.right: parent.right
    anchors.margins: 10
    height: 40
    property bool backButtonEnabled: false

    Rectangle {
        id: backButton
        width: ( backButtonEnabled ? parent.height : parent.height / 2 )
        height: parent.height
        color: "Transparent"
        Text {
            color: "#FFFFFF"
            text: ( backButtonEnabled ? "<" : "" )
            font.pixelSize: 30
            anchors.fill: parent
            horizontalAlignment: Text.AlignHCenter
        }

        MouseArea {
            anchors.fill: parent

            onClicked: {
                if (backButtonEnabled) {
                    stack.pop();
                }
            }
        }
    }

    Text {
        color: "#FFFFFF"
        text: "Cloud Password Manager"
        font.pixelSize: 30
        anchors.verticalCenter: parent.verticalCenter
        anchors.left: backButton.right
    }
}

