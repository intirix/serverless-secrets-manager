import QtQuick 2.0
import CPMQ 1.0


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

    MyHeader {
        id: header
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
            height: 50
            width: parent.width
            Text {
                id: labelWebsite
                anchors.top: parent.top
                font.pixelSize: 20
                text: ""+model.display.website
            }
            Rectangle {
                height: labelCategory.implicitHeight + 4
                width: labelCategory.implicitWidth + labelCategory.implicitHeight
                anchors.top: parent.top
                anchors.right: parent.right
                anchors.topMargin: 4
                radius: height/2
                color: model.display.categoryBackground
                Text {
                    id: labelCategory
                    font.pixelSize: 13
                    text: model.display.categoryLabel
                    color: model.display.categoryForeground
                    anchors.fill: parent
                    anchors.leftMargin: parent.height/2
                    anchors.verticalCenter: parent.verticalCenter
                }
            }
            Text {
                anchors.top: labelWebsite.bottom
                anchors.topMargin: 2
                font.pixelSize: 15
                text: ""+model.display.loginName
            }
            MouseArea {
                anchors.fill: parent
                onClicked: {
                    stack.push({item:qmlBasePath+"/ViewPassword.qml",properties: {selectedSecret: model.display.sid}})
                }
            }

        }
    }

    PasswordModel {
        id: pmodel
    }

    Rectangle {
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
            clip: true
        }
    }

    Component.onCompleted: {
        midtier.decryptSecrets();
    }
}
