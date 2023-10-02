import QtQuick
import QtQuick.Layouts
import QtQuick.Controls.Material

// Item {
Pane {
    id: menu_view

    Material.elevation: 10

    RowLayout {
        anchors.verticalCenter: parent.verticalCenter
        spacing: 10
        width: parent.width

        Label {
            text: "Total Cameras:"
        }
        Label {
            color: "darkturquoise"
            font.bold: true
            text: "" + Dashboard.cameras.length
        }
        Label {
            text: "Modbus Server IP:"
        }
        Label {
            color: "yellow"
            font.bold: true
            text: "" + Dashboard.local_ips
        }
        Label {
            text: "Port:"
        }
        Label {
            color: "yellow"
            font.bold: true
            text: "5001"
        }
        Item {
            Layout.fillWidth: true
        }
        Image {
            source: "add.png"

            MouseArea {
                anchors.fill: parent

                onClicked: add_camera()
            }
        }
    }
}
