import QtQuick
import QtQuick.Layouts
import QtQuick.Controls
import QtQuick.Controls.Material

Item {
    property var camera
    //property int index

    Rectangle {
        anchors.fill: parent
        border.color: "gray"
        border.width: 1

        MouseArea {
            anchors.fill: parent
            onClicked: (mouse) => {
                let posInGridView = Qt.point(mouse.x, mouse.y)
                let posInContentItem = mapToItem(grid.contentItem, posInGridView)
                let index = grid.indexAt(posInContentItem.x, posInContentItem.y)
                console.log("index:", index ); 
                Dashboard.edit_camera(index, 1)                           
            }
            //Dashboard.edit_camera(index)     
        }

        Text {
            anchors.centerIn: parent
            text: camera.temperature  // an element is an object of CAMERA NC 200 class, so it will have these atribute which CAMERA NC 200 class have
            color: "black"
        }

    }
}