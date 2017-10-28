import QtQuick 2.0
import CPMQ 1.0


MyPage {
    headerButtonState: "BACK"
    property string selectedSecret: ""

    ToastManager {
        id: toast
    }

    Midtier {
        id: midtier
        onMessage: {
            toast.show(message,3000);
        }
        onError: {
            toast.show(error,3000);
        }
        onUsersListed: {
            usermodel.clear();
            var list = midtier.otherUsers;
            for ( var i = 0; i < list.length; i++) {
                usermodel.append(list[i]);
            }
        }
    }

    PasswordInfo {
        id: pi
        sid: selectedSecret
    }

    ListModel {
        id: usermodel

    }

    Text {
        id: heading
        text: "Select user to share with"
        anchors.top: parent.top
        anchors.topMargin: 20
        color: "#3F51B5"
        font.pixelSize: 20
        anchors.horizontalCenter: parent.horizontalCenter
    }

    Component {
        id: userDelegate
        Rectangle {
            width: parent.width
            height: userLabel.implicitHeight + 10
            anchors.topMargin: 10
            Text {
                id: userLabel
                font.pixelSize: 20
                text: name
            }
            MouseArea {
                anchors.fill: parent
                onClicked: {
                    console.log("Clicked: "+username);
                    midtier.shareSecret(selectedSecret,username);
                }
            }
        }
    }



    Rectangle {
        anchors.top: heading.bottom
        anchors.left: parent.left
        anchors.right: parent.right
        anchors.bottom: parent.bottom
        anchors.margins: 10



        ListView {
            anchors.fill: parent
            model: usermodel
            delegate: userDelegate
            //highlight: Rectangle { color: "lightsteelblue"; radius: 5 }
            focus: true
            clip: true
        }
    }

    Component.onCompleted: {
        midtier.listUsers();
    }


}
