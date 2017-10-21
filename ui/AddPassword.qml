import QtQuick 2.0
import CPMQ 1.0


Rectangle {

    MyHeader {
        id: header
        backButtonEnabled: true
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


    Rectangle {
        anchors.top: header.bottom
        anchors.left: parent.left
        anchors.right: parent.right
        anchors.bottom: parent.bottom
        anchors.margins: 10


        MyTextInput {
            id: website
            hint: "Website"
            width: ( parent.width < 500 ? parent.width : 500 )
            anchors.horizontalCenter: parent.horizontalCenter
            anchors.top: parent.top
        }
        MyTextInput {
            id: url
            hint: "URL"
            width: ( parent.width < 500 ? parent.width : 500 )
            anchors.horizontalCenter: parent.horizontalCenter
            anchors.topMargin: 10
            anchors.top: website.bottom
        }
        MyTextInput {
            id: username
            hint: "Username"
            width: ( parent.width < 500 ? parent.width : 500 )
            anchors.horizontalCenter: parent.horizontalCenter
            anchors.topMargin: 10
            anchors.top: url.bottom
        }
        MyTextInput {
            id: password
            hint: "Password"
            width: ( parent.width < 500 ? parent.width : 500 )
            anchors.horizontalCenter: parent.horizontalCenter
            anchors.topMargin: 10
            anchors.top: username.bottom
            inputMethodHints: Qt.ImhHiddenText;
            echoMode: TextInput.Password
        }
        MyButton {
            anchors.top: password.bottom
            anchors.right: password.right
            anchors.topMargin: 10
            label: "Add"
        }









    }


}
