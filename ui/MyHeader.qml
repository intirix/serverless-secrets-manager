import QtQuick 2.0


Rectangle {
    id: header
    color: "#3F51B5"
    anchors.top: parent.top
    anchors.left: parent.left
    anchors.right: parent.right
    anchors.margins: 10
    height: 40
    property string buttonState: "NONE"
    property string headerText: "Cloud Password Manager"

    Rectangle {
        id: leftButton
        width: ( buttonState != "NONE" ? parent.height : parent.height / 2 )
        height: parent.height
        color: "Transparent"
        Text {
            color: "#FFFFFF"
            text: ( buttonState == "BACK" ? "<" : ( buttonState == "MENU" ? "\u2630" : "" ) )
            font.pixelSize: 30
            anchors.fill: parent
            horizontalAlignment: Text.AlignHCenter
            verticalAlignment: Text.AlignVCenter
        }

        MouseArea {
            anchors.fill: parent

            onClicked: {
                if (buttonState=="BACK") {
                    stack.pop();
                } else if (buttonState=="MENU") {
                    if (menu.state=="OPEN") {
                        menu.closeMenu();
                    } else {
                        menu.openMenu();
                    }
                }
            }
        }
    }

    Text {
        color: "#FFFFFF"
        text: headerText
        font.pixelSize: 30
        anchors.verticalCenter: parent.verticalCenter
        anchors.left: leftButton.right
    }
}

