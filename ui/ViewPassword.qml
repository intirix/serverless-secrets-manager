import QtQuick 2.0
import CPMQ 1.0


Rectangle {
    color: "#FF0000"
    property string selectedSecret: ""

    MyHeader {
        id: header
    }

    ToastManager {
        id: toast
    }

    Midtier {
        id: midtier
        onMessage: {
            toast.show(message,3000);
        }

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
            id: copyArea
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

        Rectangle {
            color: "#0000FF"
            anchors.top: copyArea.top
            anchors.left: copyArea.right
            anchors.leftMargin: 10
            width: copyText.implicitWidth + 10
            height: copyText.implicitHeight + 10
            Text {
                id: showText
                text: "Show"
                anchors.verticalCenter: parent.verticalCenter
                anchors.horizontalCenter: parent.horizontalCenter
            }
            MouseArea {
                anchors.fill: parent
                onClicked: {
                    if (passwordStars.visible) {
                        passwordStars.visible = false;
                        password.visible = true;
                        showText.text = "Hide";
                    } else {
                        passwordStars.visible = true;
                        password.visible = false;
                        showText.text = "Show";
                    }
                }
            }
        }

        Rectangle {
            id: indUpper
            height: 40
            width: 40
            radius: height/2
            color: ( pi.passwordHasUpper ? "#3F51B5" : "#AAAAAA" )
            anchors.top: copyArea.bottom
            anchors.left: passwordLabel.right
            anchors.topMargin: 7
            anchors.leftMargin: 12
            Text {
                text: "A"
                font.pixelSize: 30
                color: "#FFFFFF"
                anchors.verticalCenter: parent.verticalCenter
                anchors.horizontalCenter: parent.horizontalCenter
            }
        }
        Rectangle {
            id: indLower
            height: 40
            width: 40
            radius: height/2
            color: ( pi.passwordHasLower ? "#3F51B5" : "#AAAAAA" )
            anchors.top: indUpper.top
            anchors.left: indUpper.right
            anchors.leftMargin: 5
            Text {
                text: "a"
                font.pixelSize: 30
                color: "#FFFFFF"
                anchors.verticalCenter: parent.verticalCenter
                anchors.horizontalCenter: parent.horizontalCenter
            }
        }
        Rectangle {
            id: indNumber
            height: 40
            width: 40
            radius: height/2
            color: ( pi.passwordHasNumber ? "#3F51B5" : "#AAAAAA" )
            anchors.top: indLower.top
            anchors.left: indLower.right
            anchors.leftMargin: 5
            Text {
                text: "2"
                font.pixelSize: 30
                color: "#FFFFFF"
                anchors.verticalCenter: parent.verticalCenter
                anchors.horizontalCenter: parent.horizontalCenter
            }
        }
        Rectangle {
            id: indSpecial
            height: 40
            width: 40
            radius: height/2
            color: ( pi.passwordHasSpecial ? "#3F51B5" : "#AAAAAA" )
            anchors.top: indNumber.top
            anchors.left: indNumber.right
            anchors.leftMargin: 5
            Text {
                text: "$"
                font.pixelSize: 30
                color: "#FFFFFF"
                anchors.verticalCenter: parent.verticalCenter
                anchors.horizontalCenter: parent.horizontalCenter
            }
        }
        Text {
            id: categoryLabel
            font.pixelSize: 15
            text: "Category:"
            anchors.top: indUpper.bottom
            anchors.topMargin: 10
        }

        Rectangle {
            height: labelCategory.implicitHeight + 4
            width: labelCategory.implicitWidth + labelCategory.implicitHeight
            anchors.top: indUpper.bottom
            anchors.left: categoryLabel.right
            anchors.topMargin: 9
            anchors.leftMargin: 10
            radius: height/2
            color: pi.categoryBackground
            Text {
                id: labelCategory
                font.pixelSize: 13
                text: pi.categoryLabel
                color: pi.categoryForeground
                anchors.fill: parent
                anchors.leftMargin: parent.height/2
                anchors.verticalCenter: parent.verticalCenter
            }
        }


    }
}
