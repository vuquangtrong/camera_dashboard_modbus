"""
Main script
"""
import signal
import time
from nc200_camera import NC200_Camera

request_app_exit = False

def handler(signum, frame):
    """
    force app to exit
    """
    global request_app_exit
    res = input("Ctrl-c was pressed. Do you really want to exit? y/n ")
    if res == 'y':
        request_app_exit = True


signal.signal(signal.SIGINT, handler)

camera = NC200_Camera("http://127.0.0.1:5000")
camera.get_info()

if camera.login() == NC200_Camera.ERR_NONE:
    while not request_app_exit:
        time.sleep(5)
        print("Temp = ", camera.get_temperature_at(100, 100))

camera.stop_heartbeat()
