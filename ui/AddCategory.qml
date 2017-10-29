import QtQuick 2.0
import QtQuick.Controls 1.4
import CPMQ 1.0
import QtQuick.Dialogs 1.2


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
            stack.push({item:qmlBasePath+"/CategoryList.qml",replace: true})
        }
    }

    Rectangle {
        anchors.top: parent.top
        anchors.left: parent.left
        anchors.right: parent.right
        anchors.bottom: parent.bottom
        anchors.margins: 10

        property string selectedColor: "#FFFFFF"

        MyTextInput {
            id: label
            hint: "Label"
            width: ( parent.width < 500 ? parent.width : 500 )
            anchors.horizontalCenter: parent.horizontalCenter
            anchors.top: parent.top
        }
        ColorDialog {
            id: colorDialog
            title: "Select Category Background Color"
            color: "#3F51B5"
            onAccepted: {
                console.log("Selected "+colorDialog.color);
                var r = 0.299 * + 255 * colorDialog.color.r
                var b = 0.587 * + 255 * colorDialog.color.b
                var g = 0.114 * + 255 * colorDialog.color.g
                var a = 1.0 - ( ( r + g + b ) / 255.0 )
                var fg = "#000000"
                if (a>0.5) {
                    fg = "#FFFFFF"
                }
                console.log("Foreground "+fg+" for "+colorDialog.color);
                labelCategory.color = fg;
            }
        }

        Rectangle {
            id: exampleItem
            height: labelCategory.implicitHeight + 4
            width: labelCategory.implicitWidth + labelCategory.implicitHeight
            anchors.top: label.bottom
            anchors.left: label.left
            anchors.topMargin: 9
            radius: height/2
            color: colorDialog.color
            Text {
                id: labelCategory
                font.pixelSize: 13
                text: ( label.text == "" ? "Example" : label.text )
                color: "#000000"
                anchors.fill: parent
                anchors.leftMargin: parent.height/2
                verticalAlignment: Text.AlignVCenter
            }
            MouseArea {
                anchors.fill: parent
                onClicked: {
                    colorDialog.open();
                }
            }
        }



        MyButton {
            anchors.top: exampleItem.bottom
            anchors.right: label.right
            anchors.topMargin: 10
            label: "Add"
            onClicked: {
                var obj = {};
                obj.label=label.text
                obj.background=""+colorDialog.color
                midtier.addCategory(JSON.stringify(obj));
            }
        }









    }


}
