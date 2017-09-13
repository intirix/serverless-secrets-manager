import QtQuick 2.0

Rectangle {
    id: button
    radius: height * 1 / 3
    state: "NORMAL"

    property int vpadding: 10
    property int hpadding: 10
    implicitHeight: buttonLabel.implicitHeight + vpadding * 2
    implicitWidth: buttonLabel.implicitWidth + hpadding * 2

    signal clicked()

    border.color: "#3F51B5"
    border.width: 3

    property alias label: buttonLabel.text
    property color restingLabelColor: "#000000"
    property color restingColor: "#FFFFFF"
    property color pressedLabelColor: "#000000"
    property color pressedColor: "#a5c5f7"
    states: [
        State {
            name: "NORMAL"
            PropertyChanges { target: button; color: restingColor }
            PropertyChanges { target: buttonLabel; color: restingLabelColor }
        },
        State {
            name: "PRESSED"
            PropertyChanges { target: button; color: pressedColor }
            PropertyChanges { target: buttonLabel; color: pressedLabelColor }
        }
    ]

    Text {
        id: buttonLabel
        text: qsTr("text")
        anchors {
            horizontalCenter: button.horizontalCenter
            verticalCenter: button.verticalCenter
        }
    }
    MouseArea {
        anchors.fill: parent

        onPressed: {
            button.state = "PRESSED"
        }

        onClicked: {
            console.log("MyButton.onClicked()")
            button.clicked()
        }

        onReleased: {
            button.state = "NORMAL"
        }
    }
}
