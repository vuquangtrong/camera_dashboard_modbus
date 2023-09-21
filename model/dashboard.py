from PySide6.QtCore import QObject, Property, Signal, Slot
from PySide6.QtQml import qmlRegisterType

from model.camera_nc200 import Camera_NC200

import json

class Dashboard(QObject):
    """
    Dashboard Object
    """

    # SIGNALS
    camerasUpdated = Signal()

    # ATTRIBUTES

    # METHODS
    def __init__(self, parent: QObject):
        super().__init__(parent)

        # register new types to QML
        qmlRegisterType(Camera_NC200, "Camera_NC200", 1, 0,"Camera_NC200")

        # attributes

      # self._cameras = [Camera_NC200(self, ip="127.0.0.1", port=5000)] need to comment because it will override CameraNC200 class
        self._cameras =[]
        self._edittingCamera = Camera_NC200(self)
        self._isEditting = 0
        self._edittingIndex = None
        try:
            with open("database\cameras.json", "r") as file:
                json_cameras = json.load(file)
                for camera in json_cameras["cameras"]:
                    cam = Camera_NC200(self,ip=camera['ip'], port = camera['port'], modbus_server = camera['modbus_ip'], modbus_port = camera['modbus_port'])
                    self._cameras.append(cam)
        except:
            print("Error loading JSON file")

    def get_cameras(self):
        """
        get_cameras
        """
        return self._cameras

    def get_editting_camera(self):
        return self._edittingCamera

    def get_editting_index(self):
        return self._edittingIndex
    
    def get_is_editting(self):
        return self._isEditting
    

    #@Slot()
    #def add_camera(self):
        """
        show a dialog to enter new camera setting
        """
       # self._cameras.append(Camera_NC200(self, ip="127.0.0.1", port=5000)) # when added new camera, it will automatically connect with IP address and port via CAMERA NC200.py and also
       # self.camerasUpdated.emit() #append function is adding the new element is an object and it will be added to the last of the list
    
    @Slot(int, int)
    def edit_camera(self, index, is_editting):
        self._edittingIndex = index
        self._isEditting = is_editting

        if is_editting == 1:
            if index == -1:
                self._edittingCamera = Camera_NC200(self)
                self._edittingCamera.stop_query()
                self._edittingCamera.stop_heartbeat()
            else:
                self._edittingCamera = self.cameras[index]
                self._edittingCamera.stop_query()
                self._edittingCamera.stop_heartbeat()
        else:
            self._edittingCamera.start_query()
        self.camerasUpdated.emit()
        

    @Slot(int)
    def save_camera(self, index):
        if index == -1:
            self._cameras.append(self._edittingCamera)
        self.camerasUpdated.emit()
        self._edittingCamera.save_camera_to_database(index)
        #else:
            #self._camera.insert(self.edittingCamera, index)   
    # PROPERTIES

    @Slot(int)
    def delete_camera(self, index):
        if index != -1:
            self.cameras.pop(index)
        self.camerasUpdated.emit()

    
    cameras = Property("QVariantList", fget=get_cameras, notify=camerasUpdated)
    edittingCamera = Property(Camera_NC200, fget=get_editting_camera, notify=camerasUpdated)
    edittingIndex = Property(int, fget = get_editting_index, notify = camerasUpdated)
    isEditting = Property(int, fget = get_is_editting, notify = camerasUpdated)

