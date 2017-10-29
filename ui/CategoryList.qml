import QtQuick 2.0
import CPMQ 1.0


MyPage {
    headerButtonState: "MENU"
    Midtier {
        id: midtier

        onError: {
            textMessage.text = error;
        }
        onMessage: {
            textMessage.text = message;
        }
    }

    Rectangle {
        id: footer
        color: "#3F51B5"
        anchors.bottom: parent.bottom
        anchors.left: parent.left
        anchors.right: parent.right
        anchors.margins: 10
        height: textMessage.implicitHeight + 6
        visible: textMessage.text != ""
        Text {
            color: "#FFFFFF"
            id: textMessage
            anchors.left: parent.left
            anchors.topMargin: 3
            anchors.bottomMargin: 3
            anchors.leftMargin: height / 2
            anchors.verticalCenter: parent.verticalCenter
        }
    }

    Component {
        id: categoryDelegate
        Rectangle {
            height: labelBox.height + 2
            width: parent.width
            Rectangle {
                id: labelBox
                height: labelCategory.implicitHeight + 4
                width: labelCategory.implicitWidth + labelCategory.implicitHeight
                anchors.top: parent.top
                radius: height/2
                color: model.background
                Text {
                    id: labelCategory
                    font.pixelSize: 20
                    text: model.text
                    color: model.foreground
                    anchors.fill: parent
                    anchors.leftMargin: parent.height/2
                    anchors.verticalCenter: parent.verticalCenter
                }
            }
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
        anchors.bottom: ( footer.visible ? footer.top : parent.bottom )
        anchors.margins: 10

        ListView {
            anchors.fill: parent
            model: cmodel
            delegate: categoryDelegate
            highlight: Rectangle { color: "lightsteelblue"; radius: 5 }
            focus: true
            clip: true
        }
    }

    Rectangle {
        width: 60
        height: width
        radius: width/2
        anchors.right: parent.right
        anchors.bottom: ( footer.visible ? footer.top : parent.bottom )
        anchors.margins: 15
        color: "#3F51B5"
        Text {
            text: "+"
            font.pixelSize: parent.width * 7 / 8
            color: "#FFFFFF"
            anchors.verticalCenter: parent.verticalCenter
            anchors.horizontalCenter: parent.horizontalCenter
        }
        MouseArea {
            anchors.fill: parent
            onClicked: {
                stack.push({item:qmlBasePath+"/AddCategory.qml"})
            }
        }
    }
}
