import QtQuick
import QtQuick.Layouts
import QtQuick.Controls
import QtQuick.Controls.Material

Item {
    anchors.fill: parent
    RowLayout {
        anchors.fill: parent
        spacing: 0

        GridView {
            id: grid
            Layout.fillWidth: true
            Layout.fillHeight: true
            cellWidth: 150
            cellHeight: 150
            leftMargin: 1
            topMargin: 1
            model: Dashboard.cameras
            delegate: CameraNC200 {
               // index: grid.indexAt(posInContentItem.x, posInContentItem.y)
                width: grid.cellWidth
                height: grid.cellHeight
                camera: modelData /// model data = Dashboard.cameras[i] // assign modelData to camera, after that camera.temperature will get the value of each camera
            }
        }

        ColumnLayout {
            Layout.maximumWidth: 300
            Layout.fillHeight: true
            spacing: 0

            SettingsModbus {
                Layout.fillWidth: true
                Layout.fillHeight: true
            }

            SettingsCamera {
                Layout.fillWidth: true
                Layout.fillHeight: true
            }
        }
    }


    AddCameraInfor{
        id: addcamerainfor
        anchors.centerIn: parent
        camera: Dashboard.edittingCamera
        index: Dashboard.edittingIndex
        visible: Dashboard.isEditting

    }
}