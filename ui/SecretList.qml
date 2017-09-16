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
            height: 45
            Text {
                id: labelWebsite
                anchors.top: parent.top
                font.pixelSize: 20
                text: ""+model.display.website
            }
            Text {
                anchors.top: labelWebsite.bottom
                anchors.topMargin: 3
                font.pixelSize: 15
                text: ""+model.display.loginName
            }
        }
    }

    MyProxyModel {
        id: pmodel
    }

    Rectangle {
	color: "#FF0000"
        anchors.top: header.bottom
        anchors.left: parent.left
        anchors.right: parent.right
        anchors.bottom: footer.top
        anchors.margins: 10
        ListView {
            anchors.fill: parent
            model: pmodel
            delegate: passwordDelegate
            highlight: Rectangle { color: "lightsteelblue"; radius: 5 }
            focus: true

        }
    }

    Component.onCompleted: {
        midtier.decryptSecrets();
    }
}
