from PySide6.QtCore import QObject, Property, Signal, Slot
from PySide6.QtQml import qmlRegisterType

from model.camera import Camera
import json
import time


class Dashboard(QObject):

    camerasUpdated = Signal()

    def __init__(self, parent: QObject):
        super().__init__(parent)
        qmlRegisterType(Camera, "Camera", 1, 0, "Camera")

        self._new_camera = Camera(self)
        self._new_camera._thread_query_stopped = True

        self._cameras = [
            # Camera(self) for _ in range(5)
        ]
        self.load_cameras()

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
