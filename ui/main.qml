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

    StackView {
        id: stack
        initialItem: view
        anchors.fill: parent

        Component {
            id: view

            Login {
               // session: session
            }
        }
    }


}

