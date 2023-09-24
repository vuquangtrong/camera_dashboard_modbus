import time
import base64
import requests
import threading
from Crypto.PublicKey import RSA
from Crypto.Cipher import PKCS1_v1_5  # RSA-PSS
from pymodbus.client.tcp import ModbusTcpClient
from pymodbus.payload import BinaryPayloadBuilder, BinaryPayloadDecoder
from pymodbus.constants import Endian
from PySide6.QtCore import QObject, Property, Signal, Slot


class Camera(QObject):

    CMD_UNKNOWN = -1
    CMD_LOGIN = 501
    CMD_TEMPERATURE_TRACKING = 20
    CMD_TEMPERATURE_OBJECT = 520
    CMD_HEARTBEAT = 9999

    ERR_NONE = 0
    ERR_INVALID_USERNAME = 10004
    ERR_NOT_AUTHENTICATED = 10005
    ERR_NO_PERMISSION = 10007
    ERR_INVALID_PASSWORD = 10009
    ERR_LOCKED_USER = 10010
    ERR_WRONG_USER_OR_PWD = 10011

    settingUpdated = Signal()
    statusUpdated = Signal()

    def __init__(self,
                 parent: QObject,
                 ip="127.0.0.1", port=5000, user="admin", pwd="admin123",
                 modbus_ip="127.0.0.1", modbus_port=5001, modbus_regs_start=40001):
        super().__init__(parent)

        # camera
        self._ip = ip
        self._port = port
        self._user = user
        self._pwd = pwd
        self._headers = {"Content-Type": "application/json; charset=utf-8"}  # default message data type
        self._token = ""
        self._pub_key = '''-----BEGIN PUBLIC KEY-----
MIGfMA0GCSqGSIb3DQEBAQUAA4GNADCBiQKBgQCsn//YAXtvUmzfcdUSVc80NgMM
NFIc/EyzOnLKcUM6Xm+up8K7AymL6TpOpgdtxDB30GlQjK7RNwJLgNSzT7d7OXJq
382cX0V6aYXA9oeZ93bsdpiDNOMNu1ezlWZNJBS2sJoUnQl7mTGJN2b44wUcqh98
F3wPTUp/+rydh3oBkQIDAQAB
-----END PUBLIC KEY-----'''
        self._cipher_rsa = PKCS1_v1_5.new(RSA.import_key(self._pub_key))
        self._logged_in = False

        # modbus
        self._modbus_ip = modbus_ip
        self._modbus_port = modbus_port
        self._modbus_regs_start = modbus_regs_start

        self._modbus_regs_temperature_low = modbus_regs_start
        self._modbus_regs_temperature_high = modbus_regs_start + 2
        self._modbus_regs_temperature_global_min = modbus_regs_start + 4
        self._modbus_regs_temperature_global_max = modbus_regs_start + 6
        self._modbus_regs_temperature_global_avg = modbus_regs_start + 8
        self._modbus_regs_alarming = modbus_regs_start + 10

        self._modbus_client = None

        # status
        self._alarm_enabled = False
        self._alarm_temperature_high_enabled = False
        self._alarm_temperature_low_enabled = False
        self._alarm_temperature_high_value = 100.0
        self._alarm_temperature_low_value = -100.0
        self._global_temperature_max = 50.0
        self._global_temperature_min = -50.0
        self._global_temperature_avg = 0.0
        self._alarming = False

        # data process
        self._thread_query_stopped = False
        self._thread_query_paused = True
        self._thread_query = threading.Thread(target=self.query_info, daemon=True)  # auto-kill
        self._thread_query.start()

    def modbus_connect(self):
        self._modbus_client = ModbusTcpClient(self._modbus_ip, port=self._modbus_port)
        self._modbus_client.connect()

    def modbus_send(self, addr, value, type):
        if self._modbus_client is not None:
            if type == "float":
                builder = BinaryPayloadBuilder(byteorder=Endian.BIG, wordorder=Endian.LITTLE)
                builder.add_32bit_float(value)
                payload = builder.build()
                self._modbus_client.write_register(addr, value=int.from_bytes(payload[0]))
                self._modbus_client.write_register(addr+1, value=int.from_bytes(payload[1]))
            elif type == "bool":
                if value:
                    self._modbus_client.write_register(addr, value=1)
                else:
                    self._modbus_client.write_register(addr, value=0)

    def check_alarm(self):

        self._alarming = False

        if self._alarm_enabled:
            if self._alarm_temperature_high_enabled and self._global_temperature_max >= self._alarm_temperature_high_value:
                self._alarming = True
            if self._alarm_temperature_low_enabled and self._global_temperature_min <= self._alarm_temperature_low_value:
                self._alarming = True

        # forward to modbus
        self.modbus_send(self._modbus_regs_temperature_low, self._alarm_temperature_low_value, "float")
        self.modbus_send(self._modbus_regs_temperature_high, self._alarm_temperature_high_value, "float")
        self.modbus_send(self._modbus_regs_temperature_global_min, self._global_temperature_min, "float")
        self.modbus_send(self._modbus_regs_temperature_global_max, self._global_temperature_max, "float")
        self.modbus_send(self._modbus_regs_temperature_global_avg, self._global_temperature_avg, "float")
        self.modbus_send(self._modbus_regs_alarming, self._alarming, "bool")

    def encode(self, data):
        return base64.b64encode(self._cipher_rsa.encrypt(data.encode())).decode()

    def check_connection(self):
        if not self._logged_in:
            self.login()

        if (self._modbus_client is None) or (not self._modbus_client.is_socket_open()):
            self.modbus_connect()

    def post(self, msg):
        try:
            request = requests.post(
                "http://" + self.ip + ":" + str(self.port) + "/getmsginfo",
                headers=self._headers,
                json=msg,
                timeout=5  # sec
            )

            # pre-process returned code
            response = request.json()
            retcode = response["retcode"]

            if (retcode == Camera.ERR_INVALID_USERNAME or
                    retcode == Camera.ERR_INVALID_PASSWORD or
                    retcode == Camera.ERR_WRONG_USER_OR_PWD or
                    retcode == Camera.ERR_NOT_AUTHENTICATED or
                    retcode == Camera.ERR_NO_PERMISSION
                ):
                self._logged_in = False
                return None

            return response

        except Exception as e:
            print(e)

        return None

    def login(self):
        msg = {
            "action": "request",
            "cmdtype": Camera.CMD_LOGIN,
            "message": {
                "username": self._user,
                "password": self.encode(self._pwd)
            },
            "from": "root",
            "to": "box",
            "sequence": 1,
            "token": ""
        }
        response = self.post(msg)
        if response is not None:
            if response['cmdtype'] == self.CMD_LOGIN:
                if response['retcode'] == self.ERR_NONE:  # succeeded
                    message = response['message']
                    self._token = message['token']
                    self._logged_in = True

    def heartbeat(self):
        msg = {
            "action": "notify",
            "cmdtype": Camera.CMD_HEARTBEAT,
            "subtype": 0,
            "message": {},
            "sequence": 1,
            "token": self._token,
        }
        self.post(msg)

    def query_temperature_tracking(self):
        msg = {
            "action": "request",
            "cmdtype": Camera.CMD_TEMPERATURE_TRACKING,
            "message": {
                "default": 0
            },
            "from": "root",
            "to": "box",
            "sequence": 1,
            "token": self._token
        }
        response = self.post(msg)
        if response is not None:
            if response['cmdtype'] == self.CMD_TEMPERATURE_TRACKING:
                if response['retcode'] == self.ERR_NONE:  # succeeded
                    message = response['message']
                    # process values
                    self._alarm_enabled = (message['trace_flag'] == 1)
                    self._alarm_temperature_high_enabled = (message['high_flag'] == 1)
                    self._alarm_temperature_low_enabled = (message['low_flag'] == 1)
                    self._alarm_temperature_high_value = message['high_temp']
                    self._alarm_temperature_low_value = message['low_temp']

    def query_temperature_object(self):
        msg = {
            "action": "request",
            "cmdtype": Camera.CMD_TEMPERATURE_OBJECT,
            "message": {},
            "sequence": 1,
            "token": self._token,
        }
        response = self.post(msg)
        if response is not None:
            if response['cmdtype'] == self.CMD_TEMPERATURE_OBJECT:
                if response['retcode'] == self.ERR_NONE:  # succeeded
                    message = response['message']
                    # process values
                    self._global_temperature_max = message['global_max_temp']
                    self._global_temperature_min = message['global_min_temp']
                    self._global_temperature_avg = message['global_avg_temp']

                    # process alarm
                    self.check_alarm()

    def query_info(self):
        heartbeat_delay_counter = 0
        connection_delay_counter = 0

        while not self._thread_query_stopped:
            time.sleep(1)

            self.check_connection()

            while not self._thread_query_paused:
                time.sleep(1)

                connection_delay_counter += 1
                if connection_delay_counter > 5:
                    connection_delay_counter = 0
                    self.check_connection()

                # query info every second
                self.query_temperature_tracking()
                self.query_temperature_object()

                # update UI every second
                self.statusUpdated.emit()

                # send heartbeat every minute
                heartbeat_delay_counter += 1
                if heartbeat_delay_counter >= 10:
                    heartbeat_delay_counter = 0
                    self.heartbeat()

    @Slot()
    def resume_query(self):
        self._thread_query_paused = False

    @Slot()
    def pause_query(self):
        self._thread_query_paused = True

    # camera

    def get_ip(self):
        return self._ip

    def get_port(self):
        return self._port

    def get_user(self):
        return self._user

    def get_pwd(self):
        return self._pwd

    # modbus

    def get_modbus_ip(self):
        return self._modbus_ip

    def get_modbus_port(self):
        return self._modbus_port

    def get_modbus_regs_start(self):
        return self._modbus_regs_start

    @Slot(str, int, str, str,  str, int, int)
    def save_settings(self,
                      ip, port, user, pwd,
                      modbus_ip, modbus_port, modbus_regs_start):
        self._ip = ip
        self._port = port
        self._user = user
        self._pwd = pwd
        self._modbus_ip = modbus_ip
        self._modbus_port = modbus_port
        self._modbus_regs_start = modbus_regs_start
        self.statusUpdated.emit()

        # force close all old connection
        self._logged_in = False
        self._modbus_client = None

    # status

    def is_connected(self):
        return self._logged_in and self._modbus_client is not None and self._modbus_client.is_socket_open()

    def is_alarm_enabled(self):
        return self._alarm_enabled

    def is_alarm_temperature_high_enabled(self):
        return self._alarm_temperature_high_enabled

    def is_alarm_temperature_low_enabled(self):
        return self._alarm_temperature_low_enabled

    def get_alarm_temperature_high_value(self):
        return self._alarm_temperature_high_value

    def get_alarm_temperature_low_value(self):
        return self._alarm_temperature_low_value

    def get_global_temperature_max(self):
        return self._global_temperature_max

    def get_global_temperature_min(self):
        return self._global_temperature_min

    def get_global_temperature_avg(self):
        return self._global_temperature_avg

    def is_alarming(self):
        return self._alarming

    # properties

    ip = Property(str, fget=get_ip, notify=settingUpdated)
    port = Property(int, fget=get_port, notify=settingUpdated)
    user = Property(str, fget=get_user,  notify=settingUpdated)
    pwd = Property(str, fget=get_pwd, notify=settingUpdated)

    modbus_ip = Property(str, fget=get_modbus_ip, notify=settingUpdated)
    modbus_port = Property(int, fget=get_modbus_port, notify=settingUpdated)
    modbus_regs_start = Property(int, fget=get_modbus_regs_start, notify=settingUpdated)

    connected = Property(bool, fget=is_connected, notify=statusUpdated)

    alarm_enabled = Property(bool, fget=is_alarm_enabled, notify=statusUpdated)
    alarm_temperature_high_enabled = Property(bool, fget=is_alarm_temperature_high_enabled, notify=statusUpdated)
    alarm_temperature_low_enabled = Property(bool, fget=is_alarm_temperature_low_enabled, notify=statusUpdated)
    alarm_temperature_high_value = Property(float, fget=get_alarm_temperature_high_value, notify=statusUpdated)
    alarm_temperature_low_value = Property(float, fget=get_alarm_temperature_low_value, notify=statusUpdated)
    global_temperature_max = Property(float, fget=get_global_temperature_max, notify=statusUpdated)
    global_temperature_min = Property(float, fget=get_global_temperature_min, notify=statusUpdated)
    global_temperature_avg = Property(float, fget=get_global_temperature_avg, notify=statusUpdated)
    alarming = Property(bool, fget=is_alarming, notify=statusUpdated)
