from PySide6.QtCore import QObject, Property, Signal, Slot
from PySide6.QtQml import qmlRegisterType

from model.camera_nc200 import Camera_NC200


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
        qmlRegisterType(Camera_NC200, "Camera_NC200", 1, 0, "Camera_NC200")

        # attributes
        self._cameras = [Camera_NC200(self, ip="192.168.1.173", port=80)]

    def get_cameras(self):
        """
        get_cameras
        """
        return self._cameras

    @Slot()
    def add_camera(self):
        """
        show a dialog to enter new camera setting
        """
        self._cameras.append(Camera_NC200(self, ip="127.0.0.1", port=5000))
        self.camerasUpdated.emit()

    # PROPERTIES
    cameras = Property("QVariantList", fget=get_cameras, notify=camerasUpdated)
