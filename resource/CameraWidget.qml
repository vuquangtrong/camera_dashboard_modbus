import QtQuick
import QtQuick.Layouts
import QtQuick.Controls.Material

Pane {
    property var camera
    property int font_size: 20
    property int position

    Material.elevation: 10

    Label {
        anchors.left: parent.left
        anchors.top: parent.top
        font.bold: true
        font.pointSize: font_size
        opacity: 0.5
        text: "" + (position + 1)
    }
    Image {
        anchors.right: parent.right
        anchors.top: parent.top
        opacity: 0.5
        source: camera.connected ? "connected.png" : "disconnected.png"
    }
    Image {
        anchors.bottom: parent.bottom
        anchors.right: parent.right
        opacity: 0.2
        source: "adjust.png"

        MouseArea {
            anchors.fill: parent
            hoverEnabled: true

            onClicked: show_camera_settings(position)
            onEntered: parent.opacity = 1.0
            onExited: parent.opacity = 0.2
        }
    }
    Image {
        anchors.horizontalCenter: parent.horizontalCenter
        anchors.top: parent.top
        source: "warning.png"
        visible: camera.alarming

        SequentialAnimation on opacity  {
            loops: Animation.Infinite
            running: camera.alarming

            PropertyAnimation {
                duration: 500
                to: 0.0
            }
            PropertyAnimation {
                duration: 500
                to: 1.0
            }
        }
    }
    Row {
        anchors.centerIn: parent
        spacing: 4

        Label {
            Material.foreground: Material.Blue
            font.bold: true
            font.pointSize: font_size
            text: "" + camera.global_temperature_min
        }
        Label {
            Material.foreground: Material.Grey
            font.pointSize: font_size - 3
            opacity: 0.5
            text: "°C"
        }
        Label {
            Material.foreground: Material.Grey
            font.pointSize: font_size
            text: " - "
        }
        Label {
            Material.foreground: Material.Orange
            font.bold: true
            font.pointSize: font_size
            text: "" + camera.global_temperature_max
        }
        Label {
            Material.foreground: Material.Grey
            font.pointSize: font_size - 3
            opacity: 0.5
            text: "°C"
        }
    }
    Column {
        anchors.bottom: parent.bottom
        anchors.left: parent.left
        opacity: 0.5
        spacing: 4

        Row {
            spacing: 4

            Label {
                Material.foreground: Material.Grey
                text: "Min: "
            }
            Label {
                Material.foreground: Material.Blue
                text: "" + camera.alarm_temperature_low_value
            }
            Label {
                Material.foreground: Material.Grey
                text: "°C"
            }
        }
        Row {
            spacing: 4

            Label {
                Material.foreground: Material.Grey
                text: "Max: "
            }
            Label {
                Material.foreground: Material.Orange
                text: "" + camera.alarm_temperature_high_value
            }
            Label {
                Material.foreground: Material.Grey
                text: "°C"
            }
        }
    }
}
