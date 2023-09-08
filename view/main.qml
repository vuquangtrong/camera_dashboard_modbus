import QtQuick
import QtQuick.Layouts
import QtQuick.Controls
import QtQuick.Controls.Material

ApplicationWindow {
    width: 1280
    height: 720
    visible: true

    Material.theme: Material.Dark
    Material.accent: Material.Purple

    DashboardView {
        anchors.fill: parent
    }

    Text {
        anchors.left: parent.left
        anchors.bottom: parent.bottom
        text: "Cameras: " + Dashboard.cameras.length
    }
}