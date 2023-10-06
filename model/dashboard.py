import json
import time
import subprocess
import re
from PySide6.QtCore import QObject, Property, Signal, Slot
from PySide6.QtQml import qmlRegisterType

from model.camera import Camera
from model.modbus_server import Modbus_Server


class Dashboard(QObject):

    camerasUpdated = Signal()

    def __init__(self, parent: QObject):
        super().__init__(parent)
        qmlRegisterType(Camera, "Camera", 1, 0, "Camera")

        self._modbus_server = Modbus_Server()
        self._modbus_server.start()

        self._new_camera = Camera(self)
        self._new_camera._thread_query_stopped = True

        self._cameras = [
            # Camera(self) for _ in range(5)
        ]
        self.load_cameras()

    def exit(self):
        self._modbus_server.stop()

    def get_local_ips(self):
        ipconfig = subprocess.check_output('ipconfig').decode("utf-8").splitlines()
        pattern = re.compile(r'^ *IPv4 Address[.\s]*:\s*([\d.]+)\s*$')
        ips = []
        for line in ipconfig:
            result = pattern.search(line)
            if result:
                ips.append(result.group(1))
        
        return "127.0.0.1 / " + ' '.join(ips)
    
    def load_cameras(self):
        try:
            with open("cameras.json", "r") as f:
                js = json.load(f)
                for camera in js["cameras"]:
                    camera = Camera(self,
                                    camera["ip"], camera["port"], camera["user"], camera["pwd"],
                                    camera["modbus_ip"], camera["modbus_port"], camera["modbus_regs_start"])
                    camera.resume_query()
                    self._cameras.append(camera)
        except Exception as e:
            print("Error in reading JSON file", e)

    @Slot()
    def save_cameras(self):
        try:
            cameras = {
                "cameras": [
                    {
                        "ip": camera._ip,
                        "port": camera._port,
                        "user": camera._user,
                        "pwd": camera._pwd,
                        "modbus_ip": camera._modbus_ip,
                        "modbus_port": camera._modbus_port,
                        "modbus_regs_start": camera._modbus_regs_start,
                    } for camera in self._cameras
                ]
            }
            with open("cameras.json", "w") as f:
                json.dump(cameras, f, indent=2)
        except Exception as e:
            print("Error in saving JSON file", e)

    def get_new_camera(self):
        return self._new_camera

    def get_cameras(self):
        return self._cameras

    @Slot()
    def add_camera(self):
        camera = Camera(self,
                        self._new_camera._ip, self._new_camera._port, self._new_camera._user, self._new_camera._pwd,
                        self._new_camera._modbus_ip, self._new_camera._modbus_port, self._new_camera._modbus_regs_start)
        camera.resume_query()
        self._cameras.append(camera)
        self.save_cameras()
        self.camerasUpdated.emit()

    @Slot(int)
    def remove_camera(self, index):
        self._cameras[index].stop_query()
        time.sleep(2)  # wait for thread exit
        del self._cameras[index]
        self.save_cameras()
        self.camerasUpdated.emit()

    new_camera = Property(Camera, fget=get_new_camera, notify=camerasUpdated)
    cameras = Property("QVariantList", fget=get_cameras, notify=camerasUpdated)
    local_ips=Property(str, fget=get_local_ips, notify=camerasUpdated)