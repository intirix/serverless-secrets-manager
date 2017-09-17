import QtQuick 2.0
import CPMQ 1.0


Rectangle {
    color: "#FF0000"
    property string selectedSecret: ""

    MyHeader {
        id: header
    }

    PasswordInfo {
        id: pi
        sid: selectedSecret
    }

    Rectangle {
        anchors.top: header.bottom
        anchors.left: parent.left
        anchors.right: parent.right
        anchors.bottom: parent.bottom
        anchors.margins: 10
        color: "#00FF00"

        Text {
            font.pixelSize: 30
            text: pi.website
            anchors.top: parent.top
            anchors.topMargin: 5
        }

    }
}
