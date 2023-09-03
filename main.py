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

try:
    if camera.login() == NC200_Camera.ERR_NONE:
        print("Logged in")
        camera.get_temperature_at(100, 100)
        if camera.modbus_connect():
            print("Connected to Modbus")
            while not request_app_exit:
                time.sleep(1)
                temp = camera.get_temperature_at(100, 100)
                print("Temp = ", temp)
                camera.modbus_set_temp(temp)
except Exception as ex:  # catch all exceptions
    print(ex)

camera.stop_heartbeat()
camera.modbus_disconnect()
