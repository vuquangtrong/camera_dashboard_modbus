import QtQuick
import QtQuick.Layouts
import QtQuick.Controls
import QtQuick.Controls.Material

Item {
    Button {
        text: "Add Camera"
        onClicked: Dashboard.add_camera()
    }
}