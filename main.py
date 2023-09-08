"""
Camera Dashboard
"""

import sys

from PySide6.QtGui import QGuiApplication
from PySide6.QtQml import QQmlApplicationEngine

from model.dashboard import Dashboard

# new application
app = QGuiApplication(sys.argv)

# create backend
dashboard = Dashboard(app)

# create frontend engine
engine = QQmlApplicationEngine()
# get frontend context
context = engine.rootContext()
# expose backend to frontend, in qml, use the name Dashboard
context.setContextProperty('Dashboard', dashboard)
# load UI
engine.quit.connect(app.quit)
engine.load('view/main.qml')
if not engine.rootObjects():
    sys.exit(-1)

# start the app thread
sys.exit(app.exec())
