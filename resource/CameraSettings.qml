import QtQuick
import QtQuick.Layouts
import QtQuick.Controls

Dialog {
    property var camera: Dashboard.new_camera
    property int font_size: 14
    property int position: -2
    property int row_height: 30
    property int top_margin: 20
    property int left_margin_level_A: 30
    property int left_margin_level_B: 40
    property int left_margin_checkbox: 35
    property int loop_index: 0
    property bool address_is_duplicated: false
    height: camera_settings_content.height + 150
    width: camera_settings_content.width
    spacing: 20

    closePolicy: Popup.NoAutoClose
    standardButtons: Dialog.Ok | Dialog.Cancel
    title: (position >= 0 ? "CAM " + (position + 1) : "New Camera") + " Settings"

    onAccepted: {
        if(position == -1)
        {
            address_is_duplicated = false;
            console.log("add cmr");
            for(loop_index = 0; loop_index < Dashboard.cameras.length; loop_index++)
            {
                if ((parseInt(ti_modbus_address_start.text) >= Dashboard.cameras[loop_index].modbus_address_start) &&
                    (parseInt(ti_modbus_address_start.text) <= Dashboard.cameras[loop_index].modbus_address_start + 4))
                {
                    loop_index = Dashboard.cameras.length;
                    address_is_duplicated = true;
                    dialog_address_exists.visible = true;
                    console.log("value is not valid");
                }
            }

            if(address_is_duplicated == false)
            {
                console.log("saveeee");
                camera.save_settings(ip.text, parseInt(port.text), user.text, pwd.text, modbus_ip.text,
                                parseInt(modbus_port.text), parseInt(ti_modbus_address_start.text));
                if (position == -1) {
                    Dashboard.add_camera();
                } else {
                    Dashboard.save_cameras();
                }
            }
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
            color: "yellow"
            font.pointSize: font_size
            text: "Do you want to delete?"
        }
    }

    Dialog {
        id: dialog_address_exists
        anchors.centerIn: parent
        closePolicy: Popup.NoAutoClose
        height: parent.height / 2
        standardButtons: Dialog.Ok | Dialog.Cancel
        width: parent.width / 2

        Label {
            anchors.centerIn: parent
            color: "yellow"
            font.pointSize: font_size
            text: "The address value already exist"
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
        id: camera_settings_content
        anchors.centerIn: parent

        RowLayout {
            Layout.topMargin: top_margin
            Label {
                Layout.preferredWidth: 100
                font.pointSize: 18
                text: "General"
                Layout.leftMargin: left_margin_level_A
                color: "Yellow"
            }
        }
        RowLayout {
            Layout.preferredHeight: row_height

            Label {
                Layout.preferredWidth: 130
                font.pointSize: font_size
                text: "Camera IP: "
                Layout.leftMargin: left_margin_level_B
            }
            TextInput {
                id: ip

                Layout.preferredWidth: 200
                color: "darkturquoise"
                font.pointSize: font_size
                text: "" + camera.ip
            }
            Label {
                Layout.preferredWidth: 130
                font.pointSize: font_size
                text: "Port: "
            }
            TextInput {
                id: port

                Layout.preferredWidth: 200
                color: "darkturquoise"
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
                Layout.preferredWidth: 130
                font.pointSize: font_size
                text: "Username: "
                Layout.leftMargin: left_margin_level_B
            }
            TextInput {
                id: user

                Layout.preferredWidth: 200
                color: "darkturquoise"
                font.pointSize: font_size
                text: "" + camera.user
            }
            Label {
                Layout.preferredWidth: 130
                font.pointSize: font_size
                text: "Password: "
            }
            TextInput {
                id: pwd

                Layout.preferredWidth: 200
                color: "darkturquoise"
                font.pointSize: font_size
                text: "" + camera.pwd
            }
        }
        RowLayout {
            Layout.preferredHeight: row_height
            visible: false

            Label {
                Layout.preferredWidth: 130
                font.pointSize: font_size
                text: "Modbus IP: "
                Layout.leftMargin: left_margin_level_B
            }
            TextInput {
                id: modbus_ip

                Layout.preferredWidth: 200
                color: "darkturquoise"
                font.pointSize: font_size
                text: "" + camera.modbus_ip
            }
            Label {
                Layout.preferredWidth: 130
                font.pointSize: font_size
                text: "Port: "
            }
            TextInput {
                id: modbus_port

                Layout.preferredWidth: 200
                color: "darkturquoise"
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
                Layout.preferredWidth: 100
                font.pointSize: 18
                text: "Alarm"
                Layout.leftMargin: left_margin_level_A
                Layout.topMargin: 10
                Layout.bottomMargin: -10
                color: "Yellow"
            }
        }
        RowLayout {
            Layout.preferredHeight: row_height

            CheckBox {
                checked: camera.alarm_enabled
                enabled: false
                font.pointSize: font_size
                text: "Enable Alarm"
                Layout.leftMargin: left_margin_checkbox
            }
        }
        RowLayout {
            Layout.preferredHeight: row_height

            CheckBox {
                checked: camera.alarm_temperature_low_enabled
                enabled: false
                font.pointSize: font_size
                text: "Enable Low Temperature"
                Layout.leftMargin: left_margin_checkbox
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
        RowLayout {
            Layout.preferredHeight: row_height

            CheckBox {
                checked: camera.alarm_temperature_high_enabled
                enabled: false
                font.pointSize: font_size
                text: "Enable High Temperature"
                Layout.leftMargin: left_margin_checkbox
            }
            TextInput {
                Layout.preferredWidth: 50
                color: "orange"
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
            Layout.topMargin: top_margin
            Label {
                Layout.preferredWidth: 130
                font.pointSize: 18
                text: "Signal list address"
                Layout.leftMargin: left_margin_level_A
                color: "Yellow"
            }
        }
        RowLayout {
            Layout.preferredHeight: row_height

            Label {
                Layout.preferredWidth: 200
                font.pointSize: font_size
                text: "Start offset: "
                Layout.leftMargin: left_margin_level_B
            }
            TextInput {
                id: ti_modbus_address_start

                Layout.preferredWidth: 200
                color: "darkturquoise"
                font.pointSize: font_size
                text: "" + camera.modbus_regs_start
                onTextEdited: {
                    ti_modbus_address_alarming.text = parseInt(text);
                    ti_modbus_address_temperature_low.text = parseInt(text);
                    ti_modbus_address_temperature_high.text = parseInt(text);
                }
            }
        }
        RowLayout {
            Layout.preferredHeight: row_height

            Label {
                Layout.preferredWidth: 200
                font.pointSize: font_size
                color: "gray"
                text: "Alarm status: "
                Layout.leftMargin: left_margin_level_B
            }
            TextInput {
                id: ti_modbus_address_alarming

                Layout.preferredWidth: 200
                color: "darkturquoise"
                font.pointSize: font_size
                text: "" + camera.modbus_address_alarming
                readOnly: true
            }
        }
        RowLayout {
            Layout.preferredHeight: row_height

            Label {
                Layout.preferredWidth: 200
                font.pointSize: font_size
                color: "gray"
                text: "Min Temperature: "
                Layout.leftMargin: left_margin_level_B
            }
            TextInput {
                id: ti_modbus_address_temperature_low

                Layout.preferredWidth: 200
                color: "darkturquoise"
                font.pointSize: font_size
                text: "" + camera.modbus_address_temperature_low
                readOnly: true
            }
        }
        RowLayout {
            Layout.preferredHeight: row_height

            Label {
                Layout.preferredWidth: 200
                font.pointSize: font_size
                color: "gray"
                text: "Max Temperature: "
                Layout.leftMargin: left_margin_level_B
            }
            TextInput {
                id: ti_modbus_address_temperature_high

                Layout.preferredWidth: 200
                color: "darkturquoise"
                font.pointSize: font_size
                text: "" + camera.modbus_address_temperature_high
                readOnly: true
            }
        }
    }
}
