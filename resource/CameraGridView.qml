import QtQuick
import QtQuick.Layouts
import QtQuick.Controls.Material

Item {
    id: cameras_view

    property int tile_size: 300

    Flickable {
        anchors.fill: parent
        anchors.margins: 10
        contentHeight: cameras_grid.height
        visible: Dashboard.cameras.length > 0

        GridLayout {
            id: cameras_grid

            columnSpacing: 10
            columns: Math.floor(width / tile_size)
            rowSpacing: 10
            width: Math.min(Dashboard.cameras.length * tile_size, parent.width - 10)

            Repeater {
                model: Dashboard.cameras

                delegate: CameraWidget {
                    Layout.fillWidth: true
                    Layout.preferredHeight: width
                    camera: modelData // model[index]
                    position: index
                }
            }
        }
    }
    Label {
        anchors.centerIn: parent
        text: "Press (+) to add a new Camera"
        visible: Dashboard.cameras.length == 0
    }
}
