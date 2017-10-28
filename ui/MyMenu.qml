import QtQuick 2.5
import QtQuick.Window 2.2
import QtQuick.Controls 1.4

Rectangle {
    id: menu
    color: "transparent"
    z: 2
    property var header: null

    anchors.topMargin: 10
    anchors.top: header.bottom
    anchors.left: parent.left
    anchors.right: parent.right
    anchors.bottom: parent.bottom

    property int maxMenuWidth: 300
    property int menuWidth: ( parent.width < ( maxMenuWidth * 2 ) ? parent.width / 2 : maxMenuWidth )

    state: "CLOSED"

    states: [
        State {
            name: "OPEN"
            PropertyChanges { target: leftNav; width: menu.menuWidth }
            PropertyChanges { target: leftNav; x: 0 }
            PropertyChanges { target: outsideMenuArea; visible: true }
        },
        State {
            name: "CLOSED"
            PropertyChanges { target: leftNav; width: 0 }
            PropertyChanges { target: leftNav; x: -1 * menu.menuWidth }
            PropertyChanges { target: outsideMenuArea; visible: false }
        }
    ]
    transitions: Transition {
        PropertyAnimation { properties: "width,x"; easing.type: Easing.InOutQuad }
    }

    function openMenu() {
        console.log("open menu")
        menu.state = "OPEN";
    }

    function closeMenu() {
        console.log("close menu")
        menu.state = "CLOSED";
    }

    Rectangle {
        id: leftNav
        width: menu.menuWidth
        height: parent.height
        color: "#3d557c"

        StackView {
            id: menuStack
            anchors.fill: parent
        }
    }

    MouseArea {
        id: outsideMenuArea
        anchors.top: parent.top
        anchors.right: parent.right
        anchors.left: leftNav.right
        anchors.bottom: parent.bottom
        onClicked: {
            menu.closeMenu();
        }
    }
}

