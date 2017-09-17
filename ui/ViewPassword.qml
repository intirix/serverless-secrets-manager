import QtQuick 2.0
import CPMQ 1.0


Rectangle {
    color: "#FF0000"
    property string selectedSecret: ""

    MyHeader {
        id: header
    }

    Midtier {
        id: midtier
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
            id: website
            font.pixelSize: 30
            text: pi.website
            anchors.top: parent.top
            anchors.topMargin: 5
        }

        Text {
            id: loginLabel
            font.pixelSize: 15
            text: "Login Name:"
            anchors.top: website.bottom
            anchors.topMargin: 10
        }

        Text {
            id: login
            font.pixelSize: 20
            text: pi.loginName
            anchors.top: website.bottom
            anchors.left: loginLabel.right
            anchors.topMargin: 7
            anchors.leftMargin: 12
        }

        Text {
            id: passwordLabel
            font.pixelSize: 15
            text: "Password:"
            anchors.top: login.bottom
            anchors.topMargin: 10
        }

        Text {
            id: passwordStars
            font.pixelSize: 20
            text: pi.passwordStars
            anchors.top: login.bottom
            anchors.left: passwordLabel.right
            anchors.topMargin: 7
            anchors.leftMargin: 12
        }

        Text {
            id: password
            font.pixelSize: 20
            text: pi.password
            anchors.top: login.bottom
            anchors.left: passwordLabel.right
            anchors.topMargin: 7
            anchors.leftMargin: 12
            visible: false
        }

        Rectangle {
            color: "#0000FF"
            anchors.top: passwordLabel.bottom
            anchors.left: passwordLabel.right
            anchors.topMargin: 7
            anchors.leftMargin: 12
            width: copyText.implicitWidth + 10
            height: copyText.implicitHeight + 10
            Text {
                id: copyText
                text: "Copy"
                anchors.verticalCenter: parent.verticalCenter
                anchors.horizontalCenter: parent.horizontalCenter
            }
            MouseArea {
                anchors.fill: parent
                onClicked: {
                    midtier.updateClipboard(pi.password)
                }
            }
        }

    }
}
