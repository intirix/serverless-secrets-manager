import QtQuick 2.5
import QtQuick.Window 2.2
import QtQuick.Controls 1.4

Window {
    visible: true
    width: 640
    height: 480
    title: qsTr("Cloud Password Manager")

    Session {
        id: session
    }

    MyHeader {
        id: header
        buttonState: stack.currentItem.headerButtonState
    }

    MyMenu {
        id: menu
        header: header
    }

    StackView {
        id: stack
        initialItem: view
        anchors.top: header.bottom
        anchors.left: parent.left
        anchors.right: parent.right
        anchors.bottom: parent.bottom

        Component {
            id: view
            Login {
            }
        }
    }

}

