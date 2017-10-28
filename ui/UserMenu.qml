import QtQuick 2.0
import QtQuick.Controls 1.4

Item {
    ListModel {
        id: menuModel
        ListElement {
            label: "Password List"
            path: "PasswordList.qml"
        }
        ListElement {
            label: "Add Password"
            path: "AddPassword.qml"
        }
    }

    ListView {
        anchors.fill: parent

        Component {
            id: menuDelegate
            Rectangle {
                color: "#FFFFFF"
                height: menuLabel.height * 3 / 2
                width: parent.width
                Text {
                    id: menuLabel
                    anchors.leftMargin: 20
                    text: label
                    font.pixelSize: 20
                    color: "#3F51B5"
                    verticalAlignment: Text.AlignVCenter
                }
                MouseArea {
                    anchors.fill: parent
                    onClicked: {
                        stack.push({item:qmlBasePath+"/"+path})
                        menu.closeMenu();
                    }
                }
            }
        }


        model: menuModel
        delegate: menuDelegate
    }
}
