import QtQuick 2.0
import QtQuick.Controls 1.4
import CPMQ 1.0


MyPage {
    headerButtonState: "BACK"

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
        onNewPassword: {
            stack.push({item:qmlBasePath+"/ViewPassword.qml",replace: true,properties: {selectedSecret: sid}})
        }
    }

    ListModel {
        id: cmodel

        Component.onCompleted: {
            var list = midtier.categories;
            console.log(list);
            cmodel.clear()
            for ( var i = 0; i < list.length; i++) {
                cmodel.append(list[i]);
            }
        }
    }

    Rectangle {
        anchors.top: parent.top
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
        ComboBox {
            id: category
            width: ( parent.width < 500 ? parent.width : 500 )
            anchors.horizontalCenter: parent.horizontalCenter
            anchors.topMargin: 10
            anchors.top: password.bottom
            model: cmodel
            textRole: "text"
            onCurrentIndexChanged: console.debug(currentIndex+": "+currentText)

        }
        MyButton {
            anchors.top: category.bottom
            anchors.right: password.right
            anchors.topMargin: 10
            label: "Add"
            onClicked: {
                var obj = {};
                obj.website=website.text;
                obj.url=url.text;
                obj.username=username.text;
                obj.password=password.text;
                obj.category=category.currentText;
                midtier.addPassword(JSON.stringify(obj));
            }
        }









    }


}
