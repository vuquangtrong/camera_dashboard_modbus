import QtQuick
import QtQuick.Layouts
import QtQuick.Controls
import QtQuick.Controls.Material

Item {
    Button {
        text: "Add Camera"
        onClicked:{
            Dashboard.edit_camera(-1, 1)
           // addcamerainfor.visible = true
        }
    }
}
