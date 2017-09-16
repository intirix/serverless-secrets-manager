import QtQuick 2.0
import Midtier 1.0
import MyProxyModel 1.0


Item {

    Midtier {
        id: midtier

        onError: {
            textMessage.text = error;
        }
        onMessage: {
            textMessage.text = message;
        }
        onDecryptedSecret: {
            console.log("Decrypted a secret, invalidating the model")
            pmodel.invalidate();
        }
    }

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

    Rectangle {
        id: footer
        color: "#3F51B5"
        anchors.bottom: parent.bottom
        anchors.left: parent.left
        anchors.right: parent.right
        anchors.margins: 10
        height: 40

        Text {
            color: "#FFFFFF"
            id: textMessage
            anchors.margins: 3
        }
    }

    Component {
        id: passwordDelegate
        Rectangle {
            height: 40
            Column {
                Text {
                    text: " "+model.display.website
                }
            }
        }
    }

    MyProxyModel {
        id: pmodel
    }

    ListView {
        anchors.top: header.bottom
        anchors.left: parent.left
        anchors.right: parent.right
        anchors.bottom: footer.top
        anchors.margins: 10

        model: pmodel
        delegate: passwordDelegate
        highlight: Rectangle { color: "lightsteelblue"; radius: 5 }
        focus: true

    }

    Component.onCompleted: {
        midtier.decryptSecrets();
    }
}
