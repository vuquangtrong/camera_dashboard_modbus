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
            anchors.centerIn: parent
            text: camera.temperature
            color: "black"
        }

    }
}