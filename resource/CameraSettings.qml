import QtQuick
import QtQuick.Layouts
import QtQuick.Controls

Dialog {
    property var camera: Dashboard.new_camera
    property int font_size: 16
    property int position: -2
    property int row_height: 40

    closePolicy: Popup.NoAutoClose
    standardButtons: Dialog.Ok | Dialog.Cancel
    title: (position >= 0 ? "CAM " + (position + 1) : "New Camera") + " Settings"

    onAccepted: {
        camera.save_settings(ip.text, parseInt(port.text), user.text, pwd.text, modbus_ip.text, parseInt(modbus_port.text), parseInt(modbus_regs_start.text));
        if (position == -1) {
            Dashboard.add_camera();
        } else {
            Dashboard.save_cameras();
        }
    }
    onPositionChanged: {
        if (position == -1) {
            camera = Dashboard.new_camera;
        } else {
            camera = Dashboard.cameras[position];
        }
    }
    onRejected: {
        if (position == -1) {
            camera = Dashboard.new_camera;
        } else {
            camera = Dashboard.cameras[position];
        }
    }
    onVisibleChanged: {
        if (position >= 0) {
            if (visible) {
                camera.pause_query();
            } else {
                camera.resume_query();
            }
        }
    }

    Dialog {
        id: diaglog_remove

        anchors.centerIn: parent
        closePolicy: Popup.NoAutoClose
        height: parent.height / 2
        standardButtons: Dialog.Ok | Dialog.Cancel
        width: parent.width / 2

        onAccepted: {
            Dashboard.remove_camera(position);
            camera_settings.reject();
        }

        Label {
            anchors.centerIn: parent
            color: "dodgerblue"
            font.pointSize: font_size
            text: "Do you want to delete?"
        }
    }
    Image {
        anchors.right: parent.right
        anchors.top: parent.top
        source: "delete.png"
        visible: position >= 0

        MouseArea {
            anchors.fill: parent

            onClicked: {
                diaglog_remove.visible = true;
            }
        }
    }
    ColumnLayout {
        anchors.centerIn: parent

        RowLayout {
            Layout.preferredHeight: row_height

            Label {
                Layout.preferredWidth: 150
                font.pointSize: font_size
                text: "Camera IP: "
            }
            TextInput {
                id: ip

                Layout.preferredWidth: 200
                color: "dodgerblue"
                font.pointSize: font_size
                text: "" + camera.ip
            }
            Label {
                Layout.preferredWidth: 150
                font.pointSize: font_size
                text: "Port: "
            }
            TextInput {
                id: port

                Layout.preferredWidth: 200
                color: "dodgerblue"
                font.pointSize: font_size
                text: "" + camera.port

                validator: IntValidator {
                    bottom: 1
                    top: 65535
                }
            }
        }
        RowLayout {
            Layout.preferredHeight: row_height

            Label {
                Layout.preferredWidth: 150
                font.pointSize: font_size
                text: "Username: "
            }
            TextInput {
                id: user

                Layout.preferredWidth: 200
                color: "dodgerblue"
                font.pointSize: font_size
                text: "" + camera.user
            }
            Label {
                Layout.preferredWidth: 150
                font.pointSize: font_size
                text: "Password: "
            }
            TextInput {
                id: pwd

                Layout.preferredWidth: 200
                color: "dodgerblue"
                font.pointSize: font_size
                text: "" + camera.pwd
            }
        }
        RowLayout {
            Layout.preferredHeight: row_height

            Label {
                Layout.preferredWidth: 150
                font.pointSize: font_size
                text: "Modbus IP: "
            }
            TextInput {
                id: modbus_ip

                Layout.preferredWidth: 200
                color: "dodgerblue"
                font.pointSize: font_size
                text: "" + camera.modbus_ip
            }
            Label {
                Layout.preferredWidth: 150
                font.pointSize: font_size
                text: "Port: "
            }
            TextInput {
                id: modbus_port

                Layout.preferredWidth: 200
                color: "dodgerblue"
                font.pointSize: font_size
                text: "" + camera.modbus_port

                validator: IntValidator {
                    bottom: 1
                    top: 65535
                }
            }
        }
        RowLayout {
            Layout.preferredHeight: row_height

            Label {
                Layout.preferredWidth: 150
                font.pointSize: font_size
                text: "Start Register: "
            }
            TextInput {
                id: modbus_regs_start

                Layout.preferredWidth: 200
                color: "dodgerblue"
                font.pointSize: font_size
                text: "" + camera.modbus_regs_start

                validator: IntValidator {
                    bottom: 40000
                    top: 60000
                }
            }
        }
        RowLayout {
            Layout.preferredHeight: row_height

            CheckBox {
                checked: camera.alarm_enabled
                enabled: false
                font.pointSize: font_size
                text: "Enable Alarm"
            }
        }
        RowLayout {
            Layout.preferredHeight: row_height

            CheckBox {
                checked: camera.alarm_temperature_high_enabled
                enabled: false
                font.pointSize: font_size
                text: "Enable High Temperature"
            }
            TextInput {
                Layout.preferredWidth: 50
                color: "dodgerblue"
                enabled: false
                font.pointSize: font_size
                text: "" + camera.alarm_temperature_high_value
            }
            Label {
                font.pointSize: font_size
                text: "°C"
            }
        }
        RowLayout {
            Layout.preferredHeight: row_height

            CheckBox {
                checked: camera.alarm_temperature_low_enabled
                enabled: false
                font.pointSize: font_size
                text: "Enable High Temperature"
            }
            TextInput {
                Layout.preferredWidth: 50
                color: "dodgerblue"
                enabled: false
                font.pointSize: font_size
                text: "" + camera.alarm_temperature_low_value
            }
            Label {
                font.pointSize: font_size
                text: "°C"
            }
        }
    }
}
