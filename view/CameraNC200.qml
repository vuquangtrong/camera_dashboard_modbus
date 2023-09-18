import QtQuick
import QtQuick.Layouts
import QtQuick.Controls
import QtQuick.Controls.Material

Item {
    property var camera
    //property int index

    Rectangle {
        anchors.fill: parent
        border.color: "gray"
        border.width: 1

        MouseArea {
            anchors.fill: parent
            onClicked: (mouse) => {
                let posInGridView = Qt.point(mouse.x, mouse.y)
                let posInContentItem = mapToItem(grid.contentItem, posInGridView)
                let index = grid.indexAt(posInContentItem.x, posInContentItem.y)
                console.log("index:", index ); 
                Dashboard.edit_camera(index, 1)                           
            }
            //Dashboard.edit_camera(index)     
        }

        // Text {
        //     anchors.left: parent.left
        //     text: camera.temperature_min
        //     color: "green"
        // }
        // Text {
        //     anchors.right: parent.right
        //     text: camera.temperature_max
        //     color: "red"
        // }

        RowLayout {
            spacing: 2
            // width: 100
            // height: 100
            ColumnLayout {
                Text {
                    Layout.topMargin: 4
                    Layout.leftMargin: 4
                    text: "Camera " + index
                    font.family: "Time New Roman"
                }
            }
            ColumnLayout {
                Text {
                    Layout.topMargin: 4
                    Layout.leftMargin: 30
                    text: "[H " + camera.alarm_high_signal + "] / [L " + camera.alarm_low_signal + "]"
                    color: "red"
                }
            }

        }
        RowLayout {
            spacing: 2
            Text {
                Layout.topMargin: 115
                Layout.leftMargin: 4
                text: "[" + camera.temperature_low_alarm + "] " + camera.temperature_min
                color: "green"
            }
        }
        RowLayout {
            spacing: 2
            Text {
                Layout.topMargin: 130
                Layout.leftMargin: 4
                text: "[" + camera.temperature_high_alarm + "] " + camera.temperature_max
                color: "red"
            }
        }
    }
}