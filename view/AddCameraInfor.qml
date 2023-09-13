import QtQuick
import QtQuick.Layouts
import QtQuick.Window
import QtQuick.Controls
import QtQuick.Controls.Material

Item{
    property var camera
    property var index
    property var spacing_row: 20
    property var left_textfield_margin: 40
    
    Rectangle {
        anchors.centerIn: parent
        width: 500
        height: 500
        color: "black"    
        RowLayout{
            spacing: 40
            ColumnLayout{
                spacing: 10
                RowLayout{
                    spacing: spacing_row
                    Label{
                        id: lable_camera_ip
                        Layout.topMargin: 30
                        Layout.leftMargin: 20
                        Layout.preferredWidth : 25
                        Layout.preferredHeight: 25
                        text: "Camera IP:"
                        font.family: "Time New Roman"
                    }
                    TextField{
                        id: textfield_camera_ip
                        Layout.preferredWidth : 140
                        Layout.preferredHeight: 40
                    //  validator: IntValidator {}
                        Layout.leftMargin:left_textfield_margin
                        Layout.topMargin: 20
                        text: camera.property_camera_ip
                    }
                }

                RowLayout{
                    spacing: spacing_row
                    Label{
                        id: lable_camera_port
                        Layout.topMargin: 30
                        Layout.leftMargin: 20
                        Layout.preferredWidth : 25
                        Layout.preferredHeight: 25
                        text: "Camera port:"
                        font.family: "Time New Roman"
                    }
                    TextField{
                        id: textfield_camera_port
                        Layout.preferredWidth : 140
                        Layout.preferredHeight: 40
                        Layout.leftMargin:left_textfield_margin
                        Layout.topMargin: 20
                        text: camera.property_camera_port
                    }
                }

                RowLayout{
                    spacing: spacing_row
                    Label{
                        id: lable_modbus_ip
                        Layout.topMargin: 30
                        Layout.leftMargin: 20
                        Layout.preferredWidth : 25
                        Layout.preferredHeight: 25
                        text: "Modbus IP:"
                        font.family: "Time New Roman"
                    }
                    TextField{
                        id: textfield_modbus_ip
                        Layout.preferredWidth : 140
                        Layout.preferredHeight: 40
                        Layout.leftMargin:left_textfield_margin
                        Layout.topMargin: 20
                        text: camera.property_modbus_ip
                    }
                }

                RowLayout{
                    spacing: spacing_row
                    Label{
                        id: lable_modbus_port
                        Layout.topMargin: 30
                        Layout.leftMargin: 20
                        Layout.preferredWidth : 25
                        Layout.preferredHeight: 25
                        text: "Modbus port:"
                        font.family: "Time New Roman"
                    }
                    TextField{
                        id: textfield_modbus_port
                        Layout.preferredWidth : 140
                        Layout.preferredHeight: 40
                        Layout.leftMargin:left_textfield_margin
                        Layout.topMargin: 20
                        text: camera.property_modbus_port
                    }
                }

                RowLayout{
                    spacing: spacing_row
                    Label{
                        id: lable_temp_min_register
                        Layout.topMargin: 30
                        Layout.leftMargin: 20
                        Layout.preferredWidth : 25
                        Layout.preferredHeight: 25
                        text: "Temp min:"
                        font.family: "Time New Roman"
                    }
                    TextField{
                        id: textfield_temp_min_register
                        Layout.preferredWidth : 140
                        Layout.preferredHeight: 40
                        Layout.leftMargin:left_textfield_margin
                        Layout.topMargin: 20
                        text: "min"
                    }
                }

                RowLayout{
                    spacing: spacing_row
                    Label{
                        id: lable_temp_max_register
                        Layout.topMargin: 30
                        Layout.leftMargin: 20
                        Layout.preferredWidth : 25
                        Layout.preferredHeight: 25
                        text: "Temp max:"
                        font.family: "Time New Roman"
                    }
                    TextField{
                        id: textfield_temp_max_register
                        Layout.preferredWidth : 140
                        Layout.preferredHeight: 40
                        Layout.leftMargin:left_textfield_margin
                        Layout.topMargin: 20
                        text: textfield_temp_min_register.text
                    }
                }

                RowLayout{
                    spacing: 25
                    Button{
                        Layout.leftMargin: 20
                        Layout.preferredWidth : 100
                        Layout.preferredHeight: 60
                        text: "save"
                        onClicked: {
                            //check valid data
                            //no need to call edit_camera to determine editting_camera object an arrray. because it called at the same time when diaglog appear
                            //Dashboard.edit_camera(index)
                            //call edittingCamera property to get this object, which being editted
                            //get value from textfield and fill it to this object

                            camera.property_camera_ip = textfield_camera_ip.text
                            camera.property_camera_port = textfield_camera_port.text
                            camera.property_modbus_ip = textfield_modbus_ip.text
                            camera.property_modbus_port= textfield_modbus_port.text
                            
                            //need to save the data
                            Dashboard.save_camera(index)
                            Dashboard.edit_camera(1, 0)
                        }
                    }

                    Button{
                        //Layout.rightMargin: 100
                        Layout.preferredWidth : 100
                        Layout.preferredHeight: 60
                        text: "cancel"
                        onClicked: {
                            Dashboard.edit_camera(1,0)
                           
                        }
                    }
                }
           }
        //    ColumnLayout{
        //     Image{
        //         id: img_alarm
        //         source: "alarm.png"
        //         Layout.preferredWidth: 200
        //         Layout.preferredHeight: 200
        //         SequentialAnimation{
        //             running: true
        //             alwaysRunToEnd: true
        //             NumberAnimation {target: img_alarm; property:"Layout.preferredWidth"; to: 0; duration: 200}
        //             NumberAnimation {target: img_alarm; property:"Layout.preferredWidth"; to: 0; duration: 200}
        //             NumberAnimation {target: img_alarm; property:"Layout.preferredWidth"; to: 200; duration: 1000}
        //             NumberAnimation {target: img_alarm; property:"Layout.preferredWidth"; to: 200; duration: 1000}
        //         }
        //     }
        //    }
        }
    }
}