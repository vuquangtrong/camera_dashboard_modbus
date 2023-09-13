"""
Camera NC200
"""

import time
import threading
import base64
import requests
from Crypto.PublicKey import RSA
from Crypto.Cipher import PKCS1_v1_5  # RSA-PSS
from pymodbus.client.tcp import ModbusTcpClient
from pymodbus.payload import BinaryPayloadBuilder, BinaryPayloadDecoder
from pymodbus.constants import Endian
from PySide6.QtCore import QObject, Property, Signal, Slot


class Camera_NC200(QObject):
    """
    Camera NC200 Object
    """

    # SIGNALS
    temperatureUpdated = Signal()
    cameraInforUpdated1 = Signal()
    cameraInforUpdated2 = Signal()
    cameraInforUpdated3 = Signal()
    cameraInforUpdated4 = Signal()
    alarmInfoUpdate = Signal()
    alarmRulesUpdate = Signal()

    # enum for commands
    CMD_UNKNOWN = -1
    CMD_TEMP_RULES = 4
    CMD_TEMP_ALARM_INFO = 22
    CMD_INFO = 500
    CMD_LOGIN = 501
    CMD_LOGOUT = 502
    CMD_TEMP_AT_OBJ = 520
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

    ip = "192.168.1.168"  # default IP address after reset, can access via Web
    port = 80  # default HTTP port
    user = "admin"  # default username
    pwd = "admin123"  # default password for admin
    headers = {"Content-Type": "application/json; charset=utf-8"}  # default message data type

    token = ""  # will be changed on every new login
    pub_key = '''-----BEGIN PUBLIC KEY-----
MIGfMA0GCSqGSIb3DQEBAQUAA4GNADCBiQKBgQCsn//YAXtvUmzfcdUSVc80NgMM
NFIc/EyzOnLKcUM6Xm+up8K7AymL6TpOpgdtxDB30GlQjK7RNwJLgNSzT7d7OXJq
382cX0V6aYXA9oeZ93bsdpiDNOMNu1ezlWZNJBS2sJoUnQl7mTGJN2b44wUcqh98
F3wPTUp/+rydh3oBkQIDAQAB
-----END PUBLIC KEY-----'''
    cipher_rsa = None
    _heartbeat_stop = True

    modbus_server = "127.0.0.1"
    modbus_port = 5001
    modbus_client = None
    
    # METHODS
    def __init__(self,
                 parent: QObject,
                 ip="192.168.1.168",
                 port=80,
                 user="admin",
                 pwd="admin123",
                 modbus_server="127.0.0.1",
                 modbus_port=5001
                 ):
        super().__init__(parent)

        # init Camera configs
        # TODO: check param before assigning
        self.ip = ip
        self.port = port
        self.user = user
        self.pwd = pwd
        self.cipher_rsa = PKCS1_v1_5.new(RSA.import_key(self.pub_key))
        self._thread_heartbeat = threading.Thread(target=self.heartbeat, daemon=True)  # auto-kill

        # init Modbus configs
        self.modbus_server = modbus_server
        self.modbus_port = modbus_port
        self.modbus_register_max_temp = 0 # meanning 40001
        self.modbus_register_min_temp = 2
        self.modbus_register_avg_temp = 4
        self.modbus_register_alarm_setting = 6

        # init properties
        self._temperature_max = 0
        self._temperature_min = 0
        self._temperature_avg = 0
        self._alarm_enable = 0
        self._flutter_free = 0
        self._snapshot_enable = 0
        self._snapshot_type = 0
        self._record_enable = 0
        self._record_type = 0
        self._alarm_output = 0

        # start background thread
        self._thread_query_info = threading.Thread(target=self.query_info, daemon=True)  # auto-kill
        # self._thread_query_info.start()

    def encode(self, data):
        """
        encrypt password with RSA public key
        then encode encrypted password with base64
        """
        # for testing with user admin123
        # return "JwO1T3c30qOqJUkyNqo//An1ZopJ2bYZlvkj9H6Cty4kWAHc9N0eYvZnAbFb9H3Jo/hXdCvvYfwQ2+wodJJYaq4+13mu52XTVIanT2ev15aK8Oqw/S4YtMfvbOCAAZnQ+4YKXzvD2Fw71YKKmsfmi4R3Jc4E73I1jeXJId9NZiY="
        return base64.b64encode(self.cipher_rsa.encrypt(data.encode())).decode()

    def post(self, msg):
        """
        post a request with message in json format
        return response in json format also
        """
        request = requests.post(
            "http://" + self.ip + ":" + str(self.port) + "/getmsginfo",
            headers=self.headers,
            json=msg,
            timeout=5  # sec
        )

        response = request.json()
        # print(response)

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
    
    #get cmr ip
    def get_camera_ip(self):
        return self.ip
    
    #set cmr ip
    def set_camera_ip(self, camera_ip):
        # check validation of data
        if self.ip != camera_ip:
            self.ip = camera_ip
            self.cameraInforUpdated1.emit()

    #get cmr port
    def get_camera_port(self):
        return self.port
    
    #set cmmr port
    def set_camera_port(self, camera_port):
        # check data was changed or not
        if camera_port != self.port:
            self.port = camera_port
            self.cameraInforUpdated2.emit()

    #get modbus ip
    def get_modbus_ip(self):
        return self.modbus_server
    
    #set modbus ip
    def set_modbus_ip(self, modbus_ip):
        # check data was changed or not
        if self.modbus_server != modbus_ip:
            self.modbus_server = modbus_ip
            self.cameraInforUpdated3.emit()
        
    #get cmr port
    def get_modbus_port(self):
        return self.modbus_port
    
    #set cmmr port
    def set_modbus_port(self, modbus_port_1):
       #check data was changed or not
       if self.modbus_port != modbus_port_1:
            self.modbus_port = modbus_port_1
            self.cameraInforUpdated4.emit()

    def heartbeat(self):
        """
        send heartbeat every 60 seconds
        should be run on a thread using start_heartbeat 
        """
        self._heartbeat_stop = False
        seconds = 0
        while not self._heartbeat_stop:
            time.sleep(1)
            seconds += 1

            if seconds >= 60:
                seconds = 0

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
        self._thread_heartbeat.start()

    def stop_heartbeat(self):
        """
        stop the thread that sends heartbeat
        """
        self._heartbeat_stop = True

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
                return True

        return False

    def query_temperature_at(self, x, y):
        """
        query temperature at the cordinate (x,y)
        """
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
    
    def query_temperature_object(self):
        """
        query temperature at object
        """
        msg = { 
            "action":"request",
            "cmdtype": self.CMD_TEMP_AT_OBJ,
            "sequence":1,
            "token": self.token,
            "message":{}
        }

        response = self.post(msg)
        if ('cmdtype') in response and response['cmdtype'] == self.CMD_TEMP_AT_OBJ:
            if response['retcode'] == self.ERR_NONE:
                return response['message']['global_max_temp'], response['message']['global_min_temp'], response['message']['global_avg_temp']

    def query_temperature_alarm(self):
        """
        query alarm setting info
        """
        msg = {
            "action": "request",
            "cmdtype": self.CMD_TEMP_ALARM_INFO,
            "message": {
                "default": 0
            },
            "from": "root",
            "to": "box",
            "sequence": 37,
            "token": self.token
        }

        response = self.post(msg)
        if ('cmdtype') in response and response['cmdtype'] == self.CMD_TEMP_ALARM_INFO:
            if response['retcode'] == self.ERR_NONE:
                return response['message']['alarm_flag'], response['message']['alarm_shake'], response['message']['capture_flag'], response['message']['capture_stream'], response['message']['record_flag'], response['message']['record_stream'], response['message']['output_flag']

    def query_info(self):
        """
        Infinite loop to login then query info
        """
        while True:
            time.sleep(1)
            if self.login():
                    if self.modbus_connect():
                        time.sleep(1)
                        while True:
                            time.sleep(1)
                            try:
                                self.set_temperature(self.query_temperature_object())
                                self.set_temperature_alarm(self.query_temperature_alarm())
                            except:
                                print("could not set temperature to modbus")

    def get_temperature_max(self):
        """
        get_temperature
        """
        return self._temperature_max
    
    def get_temperature_min(self):
        """
        get_temperature
        """
        return self._temperature_min
    
    def get_temperature_avg(self):
        """
        get_temperature
        """
        return self._temperature_avg

    def set_temperature(self, val):
        """
        set_temperature
        """
        val_max, val_min, val_avg = val
        if val_max != self._temperature_max or val_min != self._temperature_min or val_avg != self._temperature_avg:
            self._temperature_max = val_max
            self._temperature_min = val_min
            self._temperature_avg = val_avg
            self.temperatureUpdated.emit()
            # forward to modbus
            self.modbus_set_temperature()

    def get_alarm_enable(self):
        """
        get_alarm_enable
        """
        return self._alarm_enable
    
    def get_flutter_free(self):
        """
        get_flutter_free
        """
        return self._flutter_free
    
    def get_snapshot_enable(self):
        """
        get_snapshot_enable
        """
        return self._snapshot_enable
    
    def get_snapshot_type(self):
        """
        get_snapshot_type
        """
        return self._snapshot_type
    
    def get_record_enable(self):
        """
        get_record_enable
        """
        return self._record_enable
    
    def get_record_type(self):
        """
        get_record_type
        """
        return self._record_type
    
    def get_alarm_output(self):
        """
        get_alarm_output
        """
        return self._alarm_output

    def set_temperature_alarm(self, data):
        """
        Set temperature alarm information
        """
        alarm_enable, flutter_free, snapshot_enable, snapshot_type, record_enable, record_type, alarm_output = data
        if alarm_enable != self._alarm_enable or flutter_free != self._flutter_free or snapshot_enable != self._snapshot_enable or snapshot_type != self._snapshot_type or record_enable != self._record_enable or record_type != self._record_type or alarm_output != self._alarm_output:
            self._alarm_enable = alarm_enable
            self._flutter_free = flutter_free
            self._snapshot_enable = snapshot_enable
            self._snapshot_type = snapshot_type
            self._record_enable = record_enable
            self._record_type = record_type
            self._alarm_output = alarm_output
            self.alarmInfoUpdate.emit()
            #forward to modbus
            self.modbus_update_alarm_info()


    def modbus_connect(self):
        """
        Connect to Server via Modbus TCP
        """
        self.modbus_client = ModbusTcpClient(self.modbus_server, port=self.modbus_port)
        self.modbus_client.connect()
        return self.modbus_client.is_socket_open()

    def modbus_disconnect(self):
        """
        Disconnect to Server
        """
        if self.modbus_client is not None and self.modbus_client.is_socket_open():
            self.modbus_client.close()

    def modbus_set_temperature(self):
        """
        Write temperature to a register
        """
        if self.modbus_client is not None and self.modbus_client.is_socket_open:
            builder = BinaryPayloadBuilder(byteorder=Endian.BIG, wordorder=Endian.LITTLE)
            builder.add_32bit_float(self._temperature_max)
            payload = builder.build()
            print(payload)
            self.modbus_client.write_register(address=self.modbus_register_max_temp, value=int.from_bytes(payload[0]))
            self.modbus_client.write_register(address=self.modbus_register_max_temp+1, value=int.from_bytes(payload[1]))
            res = self.modbus_client.read_holding_registers(address=self.modbus_register_max_temp, count=2)
            for r in res.registers:
                print(hex(r))
            # _builder.add_32bit_float(self._temp_min)
            # _payload = _builder.build()
            # self.modbus_client.write_registers(address=self.modbus_register_min_temp, value=_payload)
            # _builder.add_32bit_float(self._temp_avg)
            # _payload = _builder.build()
            # self.modbus_client.write_registers(address=self.modbus_register_avg_temp, value= _payload)

            # Read values in registers
            # self.modbus_client.read_holding_registers(address=self.modbus_register_max_temp, count=2)
            # _decoder = BinaryPayloadDecoder.fromRegisters(self.modbus_register_max_temp, byteorder=Endian.BIG, wordorder=Endian.LITTLE)
            # print(_decoder.decode_32bit_float)

            # self.modbus_client.read_holding_registers(address=self.modbus_register_min_temp, count=2)
            # self.modbus_client.read_holding_registers(address=self.modbus_register_avg_temp, count=2)

    def modbus_update_alarm_info(self):
        if self.modbus_client is not None and self.modbus_client.is_socket_open:
            # Write values to registers
            self.modbus_client.write_register(address=self.modbus_register_alarm_setting, value=self._alarm_enable)
            self.modbus_client.write_register(address=self.modbus_register_alarm_setting+1, value=self._flutter_free)
            self.modbus_client.write_register(address=self.modbus_register_alarm_setting+2, value=self._snapshot_enable)
            self.modbus_client.write_register(address=self.modbus_register_alarm_setting+3, value=self._snapshot_type)
            self.modbus_client.write_register(address=self.modbus_register_alarm_setting+4, value=self._record_enable)
            self.modbus_client.write_register(address=self.modbus_register_alarm_setting+5, value=self._record_type)
            self.modbus_client.write_register(address=self.modbus_register_alarm_setting+6, value=self._alarm_output)
        
            # Read values in registers
            result = self.modbus_client.read_holding_registers(address=self.modbus_register_alarm_setting, count=7)
            print(result.registers)




    # PROPERTIES
    temperature_max = Property(float, fget=get_temperature_max, notify=temperatureUpdated)
    temperature_min = Property(float, fget=get_temperature_min, notify=temperatureUpdated)
    # temperature_avg = Property(float, fget=get_temperature_avg, notify=temperatureUpdated)
    alarm_enable = Property(int, fset = get_alarm_enable, notify=alarmInfoUpdate)
    flutter_free = Property(int, fset = get_flutter_free, notify=alarmInfoUpdate)
    snapshot_enable = Property(int, fset = get_snapshot_enable, notify=alarmInfoUpdate)
    snapshot_type = Property(int, fset = get_snapshot_type, notify=alarmInfoUpdate)
    record_enable = Property(int, fset = get_record_enable, notify=alarmInfoUpdate)
    record_type = Property(int, fset = get_record_type, notify=alarmInfoUpdate)
    alarm_output = Property(int, fset = get_alarm_output, notify=alarmInfoUpdate)
    #need to export property to handler in text field
    property_camera_ip = Property(str, fset=set_camera_ip, fget=get_camera_ip, notify = cameraInforUpdated1)
    property_camera_port = Property(int, fset=set_camera_port, fget=get_camera_port,notify=cameraInforUpdated2)
    property_modbus_ip = Property(str, fset=set_modbus_ip, fget=get_modbus_ip, notify = cameraInforUpdated3)
    property_modbus_port = Property(int,fset=set_modbus_port, fget=get_modbus_port,notify = cameraInforUpdated4)
