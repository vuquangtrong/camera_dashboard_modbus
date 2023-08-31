"""
NC200 Thermal Camera
"""

import threading
import base64
import time
import requests
from Crypto.PublicKey import RSA
from Crypto.Cipher import PKCS1_v1_5  # RSA-PSS


class NC200_Camera:
    """
    NC200 Thermal Camera Object
    """

    # enum for commands
    CMD_UNKNOWN = -1
    CMD_INFO = 500
    CMD_LOGIN = 501
    CMD_LOGOUT = 502
    CMD_TEMP_AT_POINT = 521
    CMD_HEARTBEAT = 9999

    # enum for errors
    ERR_NONE = 0
    ERR_UNKNOWN = 1000
    ERR_UNCONFIGURED = 1001
    ERR_WRONG_PARAMS = 1002

    # attributes
    width = 512
    height = 384

    url = "http://192.168.1.168"  # default IP address after reset, can access via Web
    user = "admin"  # default username
    pwd = "admin123"  # default password for admin
    # default message data type
    headers = {"Content-Type": "application/json; charset=utf-8"}

    token = ""  # will be changed on every new login
    pub_key = '''-----BEGIN PUBLIC KEY-----
MIGfMA0GCSqGSIb3DQEBAQUAA4GNADCBiQKBgQCsn//YAXtvUmzfcdUSVc80NgMM
NFIc/EyzOnLKcUM6Xm+up8K7AymL6TpOpgdtxDB30GlQjK7RNwJLgNSzT7d7OXJq
382cX0V6aYXA9oeZ93bsdpiDNOMNu1ezlWZNJBS2sJoUnQl7mTGJN2b44wUcqh98
F3wPTUp/+rydh3oBkQIDAQAB
-----END PUBLIC KEY-----'''
    cipher_rsa = None

    def __init__(self, url="http://192.168.1.168", user="admin", pwd="admin123") -> None:
        """
        init the object with url and credentials
        default values are used if no param given
        """
        self.url = url
        self.user = user
        self.pwd = pwd
        self.cipher_rsa = PKCS1_v1_5.new(RSA.import_key(self.pub_key))
        self.thread_heartbeat = threading.Thread(target=self.heartbeat)
        self.thread_heartbeat_stop = False

    def encode(self, data):
        """
        encrypt password with RSA public key
        then encode encrypted password with base64
        """
        if self.cipher_rsa is None:
            return ""

        # for testing with user admin123
        # return "JwO1T3c30qOqJUkyNqo//An1ZopJ2bYZlvkj9H6Cty4kWAHc9N0eYvZnAbFb9H3Jo/hXdCvvYfwQ2+wodJJYaq4+13mu52XTVIanT2ev15aK8Oqw/S4YtMfvbOCAAZnQ+4YKXzvD2Fw71YKKmsfmi4R3Jc4E73I1jeXJId9NZiY="
        return base64.b64encode(self.cipher_rsa.encrypt(data.encode())).decode()

    def post(self, msg):
        """
        post a request with message in json format
        return response in json format also
        """
        if self.url is None:
            return {
                'cmdtype': self.CMD_UNKNOWN
            }

        request = requests.post(
            self.url + "/getmsginfo",
            headers=self.headers,
            json=msg,
            timeout=5 # sec
        )

        response = request.json()
        print(response)

        return response

    def get_info(self):
        """
        get general info and settings from camera
        """

        # construct message fields
        msg = {
            "action": "request",
            "cmdtype": self.CMD_INFO,
            "sequence": 1,
            "message": {
            }
        }

        # post request to camera
        self.post(msg)

    def heartbeat(self):
        """
        send heartbeat every 60 seconds
        should be run on a thread using start_heartbeat 
        """
        self.thread_heartbeat_stop = False
        seconds = 0
        while not self.thread_heartbeat_stop:
            time.sleep(1)
            seconds += 1

            if seconds >= 5:
                seconds = 0

                if self.url is None:
                    continue

                msg = {
                    "action": "notify",
                    "cmdtype": self.CMD_HEARTBEAT,
                    "sequence": 1,
                    "token": self.token,
                    "subtype": 0,
                    "message": {}
                }

                self.post(msg)

        print("Heartbeat is stopped!")

    def start_heartbeat(self):
        """
        start a thread to send heartbeat
        """
        self.thread_heartbeat.start()

    def stop_heartbeat(self):
        """
        stop the thread that sends heartbeat
        """
        self.thread_heartbeat_stop = True

    def login(self):
        """
        request login to camera
        save the session token
        """
        msg = {
            "action": "request",
            "cmdtype": self.CMD_LOGIN,
            "message": {
                "username": self.user,
                "password": self.encode(self.pwd)
            },
            "from": "root",
            "to": "box",
            "sequence": 1,
            "token": ""
        }

        response = self.post(msg)
        if response['cmdtype'] == self.CMD_LOGIN:
            if response['retcode'] == self.ERR_NONE:  # succeeded
                self.token = response['message']['token']
                self.start_heartbeat()
                return self.ERR_NONE
            else:
                print(response['retmsg'])
                return response['retcode']
        else:
            return self.ERR_UNCONFIGURED

    def get_temperature_at(self, x, y):
        """
        get temperature at the cordinate (x,y)
        """
        if (x < 1 or x > self.width) or (y < 1 or y > self.height):
            return self.ERR_WRONG_PARAMS

        if (self.url is None) or (self.token == ''):
            return self.ERR_UNCONFIGURED

        msg = {
            "action": "request",
            "cmdtype": self.CMD_TEMP_AT_POINT,
            "sequence": 1,
            "token": self.token,
            "message": {
                "cursor_type": 0,
                "cursor_x": x,
                "cursor_y": y
            }
        }

        response = self.post(msg)
        if 'cmdtype' in response and response['cmdtype'] == self.CMD_TEMP_AT_POINT:
            if response['retcode'] == self.ERR_NONE:
                return response['message']['value']

        return -1
