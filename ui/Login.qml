import QtQuick 2.0
import Midtier 1.0

Item {


    Midtier {
        id: midtier

        onError: {
            errorMessage.text = error;
            infoMessage.text = '';
        }
        onMessage: {
            infoMessage.text = message;
        }

        onDownloadKey: {
            storage.setItem('lastUser', midtier.user);
            storage.setItem('lastUrl', midtier.url);
            storage.setItem("encryptedPrivateKey-"+username.text, encryptedPrivateKey);
            midtier.getSecrets()
        }
    }

    Storage {
        id: storage
    }

    Rectangle {
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

    Rectangle {
        anchors.verticalCenter: parent.verticalCenter
        width: parent.width
        height: ( url.height + username.height + password.height ) * 3 / 2
        color: "transparent"

        MyTextInput {
            id: url
            text: session.getUrl()
            KeyNavigation.tab: username
        }
        MyTextInput {
            id: username
            text: session.user
            anchors.top: url.bottom
            anchors.topMargin: url.height / 2
            KeyNavigation.tab: password
        }
        MyTextInput {
            id: password
            text: session.pass
            anchors.top: username.bottom
            anchors.topMargin: username.height / 2
            inputMethodHints: Qt.ImhHiddenText;
            echoMode: TextInput.Password
            KeyNavigation.tab: login
        }
        MyButton {
            id: login
            anchors.top: password.bottom
            anchors.right: password.right
            anchors.topMargin: password.height / 2
            label: "Login"

            onClicked: {
                midtier.url = url.text;
                midtier.user = username.text
                midtier.password = password.text;
                if (storage.hasItem("encryptedPrivateKey-"+username.text)) {
                    midtier.encryptedPrivateKey = storage.getItem("encryptedPrivateKey-"+username.text,null);
                    console.log("Already have encrypted private key");
                    midtier.getSecrets();

                } else {
                    midtier.downloadPrivateKey();
                }
            }
        }

        Text {
            id: errorMessage
            anchors.top: login.bottom
            anchors.right: login.right
            anchors.left: password.left
        }

        Text {
            id: infoMessage
            anchors.top: login.bottom
            anchors.right: login.right
            anchors.left: password.left
        }
    }
}
