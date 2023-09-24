import QtQuick
import QtQuick.Layouts
import QtQuick.Controls.Material

ApplicationWindow {
    function add_camera() {
        camera_settings.position = -1;
        camera_settings.visible = true;
    }
    function show_camera_settings(index) {
        camera_settings.position = index;
        camera_settings.visible = true;
    }

    Material.theme: Material.Dark
    title: "Camera Dashboard"
    visibility: Window.Maximized
    visible: true

    ColumnLayout {
        anchors.fill: parent

        CameraGridView {
            Layout.fillHeight: true
            Layout.fillWidth: true
        }
        MenuView {
            Layout.fillWidth: true
            Layout.preferredHeight: 60
        }
    }
    CameraSettings {
        id: camera_settings

        anchors.centerIn: parent
        height: parent.height / 2
        width: parent.width / 2
    }
}
