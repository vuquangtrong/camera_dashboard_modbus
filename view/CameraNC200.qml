import QtQuick
import QtQuick.Layouts
import QtQuick.Controls
import QtQuick.Controls.Material

Item {
    property var camera

    Rectangle {
        anchors.fill: parent
        border.color: "gray"
        border.width: 1

        Text {
            anchors.left: parent.left
            text: camera.temperature_min
            color: "green"
        }
        Text {
            anchors.right: parent.right
            text: camera.temperature_max
            color: "red"
        }
    }
}