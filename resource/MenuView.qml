import QtQuick
import QtQuick.Layouts
import QtQuick.Controls.Material

// Pane {
Item {
    id: menu_view

    // Material.background: Material.BlueGrey
    // Material.elevation: 10

    Label {
        anchors.left: parent.left
        anchors.margins: 10
        anchors.verticalCenter: parent.verticalCenter
        text: "Total Cameras: " + Dashboard.cameras.length
    }
    Image {
        anchors.margins: 20
        anchors.right: parent.right
        anchors.verticalCenter: parent.verticalCenter
        source: "add.png"

        MouseArea {
            anchors.fill: parent

            onClicked: add_camera()
        }
    }
}
