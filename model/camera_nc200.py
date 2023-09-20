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
import json

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
    cameraInforUpdated5 = Signal()
    alarmTrackingUpdated = Signal()
    alarmSignalsUpdated = Signal()

    # enum for commands
    CMD_UNKNOWN = -1
    CMD_TEMP_ALARM = 48
    CMD_TEMP_TRACKING = 20
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
    _alarm_high_stop = True
    _alarm_low_stop = True

    modbus_server = "127.0.0.1"
    modbus_port = 5001
    modbus_client = None
    query_status = 0

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
        self.modbus_register_temp_max = 1 # meanning 40001
        self.modbus_register_temp_min = 3
        # self.modbus_register_avg_temp = 4
        self.modbus_register_alarm_enable = 5
        self.modbus_register_alarm_high = 6
        self.modbus_register_alarm_low = 7
        self.modbus_register_alarm_signal_high = 8
        self.modbus_register_alarm_signal_low = 9
        self.modbus_register_alarm_temp_high = 10
        self.modbus_register_alarm_temp_low = 12

        # init properties
        self._temperature_max = 0
        self._temperature_min = 0
        # self._temperature_avg = 0
        self._alarm_enable = 0
        self._alarm_shake = 0
        self._record_delay = 0
        self._alarm_flag_high = 0
        self._alarm_flag_low = 0
        self._alarm_temperature_high = 0
        self._alarm_temperature_low = 0
        self._alarm_signal_high = 0
        self._alarm_signal_low = 0
        self._qtime_high = 0   # dejiter
        self._qtime_low = 0    # dejiter
        self.query_status = 1

        # start background thread
        self._thread_query_info = threading.Thread(target=self.query_info, daemon=True)  # auto-kill
        self._thread_query_info.start()

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

    def get_offset_address_register(self):
        return self.modbus_register_temp_max
    
    def set_offset_address_register(self, offset_address_value):
        if self.modbus_register_temp_max != offset_address_value:
            self.modbus_register_temp_max = offset_address_value
            self.cameraInforUpdated5.emit()

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
                message = response['message']
                return message['global_max_temp'], message['global_min_temp'], message['global_avg_temp']

    def query_temperature_tracking(self):
        """
        query alarm for temperature spot tracking
        """
        msg = {
            "action": "request",
            "cmdtype": self.CMD_TEMP_TRACKING,
            "message": {
                "default": 0
            },
            "from": "root",
            "to": "box",
            "sequence": 34,
            "token": self.token
        }
        response = self.post(msg)
        if ('cmdtype') in response and response['cmdtype'] == self.CMD_TEMP_TRACKING:
            if response['retcode'] == self.ERR_NONE:
                message = response['message']
                return message['trace_flag'], message['alarm_shake'], message['record_delay'], message['high_flag'], message['low_flag'], message['high_temp'], message['low_temp']

    def query_info(self):
        """
        Infinite loop to login then query info
        """
        while True:
            time.sleep(1)
            while self.query_status == 1:
                if self.login():
                        time.sleep(1)
                        if self.modbus_connect():
                            time.sleep(1)
                            while self.query_status == 1:
                                try:
                                    # send temperature min, max to UI and modbus
                                    self.set_temperature(self.query_temperature_object())
                                    # send alarm temperature info to UI and modbus
                                    self.set_alarm_temperature_tracking(self.query_temperature_tracking())
                                    # send alarm signal to UI and modbus
                                    self.set_alarm_signal()
                                except:
                                    print("could not set temperature to modbus")
                else:
                    print("login failed")
                    self.query_status == 0

    def start_query(self):
        """
        start querying information
        """
        self.query_status = 1

    def stop_query(self):
        """
        stop querying information
        """
        self.query_status = 0


    def get_temperature_max(self):
        """
        get_temperature max
        """
        return self._temperature_max
    
    def get_temperature_min(self):
        """
        get_temperature min
        """
        return self._temperature_min
    
    # def get_temperature_avg(self):
    #     """
    #     get_temperature
    #     """
    #     return self._temperature_avg

    def set_temperature(self, val):
        """
        set_temperature
        """
        val_max, val_min, val_avg = val
        # if val_max != self._temperature_max or val_min != self._temperature_min or val_avg != self._temperature_avg:
        if val_max != self._temperature_max or val_min != self._temperature_min:
            self._temperature_max = val_max
            self._temperature_min = val_min
            # self._temperature_avg = val_avg
            self.temperatureUpdated.emit()
            # forward to modbus
            self.modbus_update_temperature()

    def get_alarm_enable(self):
        """
        get_alarm_enable
        """
        return self._alarm_enable
    
    def get_alarm_flag_high(self):
        """
        get_alarm high temp flag
        """
        return self._alarm_flag_high
    
    def get_alarm_flag_low(self):
        """
        get_alarm low temp flag
        """
        return self._alarm_flag_low

    def get_alarm_temperature_high(self):
        """
        get_alarm high temp
        """
        return self._alarm_temperature_high
    
    def get_alarm_temperature_low(self):
        """
        get_alarm low temp
        """
        return self._alarm_temperature_low

    def set_alarm_temperature_tracking(self, data):
        """
        Set temperature alarm information
        """
        trace_enable, alarm_shake, record_delay, high_flag, low_flag, high_temp, low_temp = data
        if trace_enable != self._alarm_enable or alarm_shake != self._alarm_shake or high_flag != self._alarm_flag_high or low_flag != self._alarm_flag_low or high_temp != self._alarm_temperature_high or low_temp != self._alarm_temperature_low:
            self._alarm_enable = trace_enable
            self._alarm_shake = alarm_shake
            self._record_delay = record_delay
            self._alarm_flag_high = high_flag
            self._alarm_flag_low = low_flag
            self._alarm_temperature_high = high_temp
            self._alarm_temperature_low = low_temp
            self.alarmTrackingUpdated.emit()
            #forward to modbus
            self.modbus_update_alarm_tracking()

    def get_alarm_signal_high(self):
        """
        get_alarm high temp signal
        """
        return self._alarm_signal_high
    
    def get_alarm_signal_low(self):
        """
        get_alarm low temp signal
        """
        return self._alarm_signal_low

    def set_alarm_signal(self):
        """
        Set temperature alarm information
        """
        if self._alarm_enable and self._alarm_flag_high and self._temperature_max >= self._alarm_temperature_high:
            if self._alarm_signal_high != 1:
                self._qtime_high += 1
        else:
            self._qtime_high = 0
            self._alarm_signal_high = 0

        if self._qtime_high >= (self._alarm_shake + self._record_delay):
            self._alarm_signal_high = 1

        if self._alarm_enable and self._alarm_flag_low and self._temperature_min <= self._alarm_temperature_low:
            if self._alarm_signal_low != 1:
                self._qtime_low += 1
        else:
            self._qtime_low = 0
            self._alarm_signal_low = 0

        if self._qtime_low >= (self._alarm_shake + self._record_delay):
            self._alarm_signal_low = 1

        self.alarmSignalsUpdated.emit()
        self.modbus_update_alarm_signal()
    
    def modbus_connect(self):
        """
        Connect to Server via Modbus TCP
        """
        self.modbus_client = ModbusTcpClient(self.modbus_server, port=self.modbus_port)
        self.modbus_client.connect()
        return self.modbus_client.is_socket_open()
    
    def get_query_status(self):
        """
        get query status
        """
        return self.query_status

    def modbus_disconnect(self):
        """
        Disconnect to Server
        """
        if self.modbus_client is not None and self.modbus_client.is_socket_open():
            self.modbus_client.close()

    def modbus_update_temperature(self):
        """
        Write temperature to a register
        """
        if self.modbus_client is not None and self.modbus_client.is_socket_open:
            builder = BinaryPayloadBuilder(byteorder=Endian.BIG, wordorder=Endian.LITTLE)
            builder.add_32bit_float(self._temperature_max)
            payload = builder.build()
            self.modbus_client.write_register(address=self.modbus_register_temp_max, value=int.from_bytes(payload[0]))
            self.modbus_client.write_register(address=self.modbus_register_temp_max+1, value=int.from_bytes(payload[1]))

            builder = BinaryPayloadBuilder(byteorder=Endian.BIG, wordorder=Endian.LITTLE)
            builder.add_32bit_float(self._temperature_min)
            payload = builder.build()
            self.modbus_client.write_register(address=self.modbus_register_temp_min, value=int.from_bytes(payload[0]))
            self.modbus_client.write_register(address=self.modbus_register_temp_min+1, value=int.from_bytes(payload[1]))

            # # Read values in registers
            # value = self.modbus_client.read_holding_registers(address=self.modbus_register_temp_max, count=2)
            # decoder = BinaryPayloadDecoder.fromRegisters(value.registers, byteorder=Endian.BIG, wordorder=Endian.LITTLE)
            # value = decoder.decode_32bit_float()
            # print(value)

            # value = self.modbus_client.read_holding_registers(address=self.modbus_register_temp_min, count=2)
            # decoder = BinaryPayloadDecoder.fromRegisters(value.registers, byteorder=Endian.BIG, wordorder=Endian.LITTLE)
            # value = decoder.decode_32bit_float()
            # print(value)

    def modbus_update_alarm_tracking(self):
        """
        Write temperature tracking to a register
        """
        if self.modbus_client is not None and self.modbus_client.is_socket_open:
            # Write values to registers
            self.modbus_client.write_register(address=self.modbus_register_alarm_enable, value=self._alarm_enable)
            self.modbus_client.write_register(address=self.modbus_register_alarm_high, value=self._alarm_flag_high)
            self.modbus_client.write_register(address=self.modbus_register_alarm_low, value=self._alarm_flag_low)

            builder = BinaryPayloadBuilder(byteorder=Endian.BIG, wordorder=Endian.LITTLE)
            builder.add_32bit_float(self._alarm_temperature_high)
            payload = builder.build()
            self.modbus_client.write_register(address=self.modbus_register_alarm_temp_high, value=int.from_bytes(payload[0]))
            self.modbus_client.write_register(address=self.modbus_register_alarm_temp_high+1, value=int.from_bytes(payload[1]))

            builder = BinaryPayloadBuilder(byteorder=Endian.BIG, wordorder=Endian.LITTLE)
            builder.add_32bit_float(self._alarm_temperature_low)
            payload = builder.build()
            self.modbus_client.write_register(address=self.modbus_register_alarm_temp_low, value=int.from_bytes(payload[0]))
            self.modbus_client.write_register(address=self.modbus_register_alarm_temp_low+1, value=int.from_bytes(payload[1]))

            # # Read values in registers
            # alarm_enable = self.modbus_client.read_holding_registers(address=self.modbus_register_alarm_enable, count=1)
            # alarm_high = self.modbus_client.read_holding_registers(address=self.modbus_register_alarm_high, count=1)
            # alarm_low = self.modbus_client.read_holding_registers(address=self.modbus_register_alarm_low, count=1)

            # value = self.modbus_client.read_holding_registers(address=self.modbus_register_alarm_temp_high, count=2)
            # decoder = BinaryPayloadDecoder.fromRegisters(value.registers, byteorder=Endian.BIG, wordorder=Endian.LITTLE)
            # value = decoder.decode_32bit_float()
            # print(value)

            # value = self.modbus_client.read_holding_registers(address=self.modbus_register_alarm_temp_low, count=2)
            # decoder = BinaryPayloadDecoder.fromRegisters(value.registers, byteorder=Endian.BIG, wordorder=Endian.LITTLE)
            # value = decoder.decode_32bit_float()
            # print(value)

    def modbus_update_alarm_signal(self):
        if self.modbus_client is not None and self.modbus_client.is_socket_open:
            # Write values to registers
            self.modbus_client.write_register(address=self.modbus_register_alarm_signal_high, value=self._alarm_signal_high)
            self.modbus_client.write_register(address=self.modbus_register_alarm_signal_low, value=self._alarm_signal_low)

            # # Read values in registers
            # signal_high = self.modbus_client.read_holding_registers(address=self.modbus_register_alarm_signal_high, count=1)
            # signal_low = self.modbus_client.read_holding_registers(address=self.modbus_register_alarm_signal_low, count=1)
    
    
    
    def save_camera_to_database(self, index):
        try:
            with open("database\cameras.json", "r") as file:
                json_cameras = json.load(file)
                if index != -1:
                    for camera in json_cameras["cameras"]:
                        print(camera["index"])
                        print(index)
                        if camera["index"] == index:
                            camera["ip"] = self.ip
                            camera["port"] = self.port
                            camera["modbus_port"] = self.modbus_port
                            camera["modbus_ip"] = self.modbus_server
                else:
                    print(len(json_cameras["cameras"]))             
                    camera = {'ip': self.ip, 'port': self.port, 'modbus_port': self.modbus_port, 'modbus_ip': self.modbus_server, 'index': len(json_cameras["cameras"])}
                    json_cameras["cameras"].append(camera)
            with open('database\cameras.json', "w") as file:
                json.dump(json_cameras, file, indent=2)
        except:
            print("Could not save camera to database")
    ### PROPERTIES
    temperature_max = Property(float, fget=get_temperature_max, notify=temperatureUpdated)
    temperature_min = Property(float, fget=get_temperature_min, notify=temperatureUpdated)
    # temperature_avg = Property(float, fget=get_temperature_avg, notify=temperatureUpdated)
    alarm_enable = Property(int, fget = get_alarm_enable, notify=alarmTrackingUpdated)
    alarm_flag_high = Property(int, fget=get_alarm_flag_high, notify=alarmTrackingUpdated)
    alarm_flag_low = Property(int, fget=get_alarm_flag_low, notify=alarmTrackingUpdated)
    alarm_temperature_high = Property(float, fget=get_alarm_temperature_high, notify=alarmTrackingUpdated)
    alarm_temperature_low = Property(float, fget=get_alarm_temperature_low, notify=alarmTrackingUpdated)
    alarm_signal_high = Property(int,fget=get_alarm_signal_high, notify=alarmSignalsUpdated)
    alarm_signal_low = Property(int,fget=get_alarm_signal_low, notify=alarmSignalsUpdated)
    #need to export property to handler in text field
    property_camera_ip = Property(str, fset=set_camera_ip, fget=get_camera_ip, notify = cameraInforUpdated1)
    property_camera_port = Property(int, fset=set_camera_port, fget=get_camera_port,notify=cameraInforUpdated2)
    property_modbus_ip = Property(str, fset=set_modbus_ip, fget=get_modbus_ip, notify = cameraInforUpdated3)
    property_modbus_port = Property(int,fset=set_modbus_port, fget=get_modbus_port,notify = cameraInforUpdated4)
    property_offset_address_register = Property(int, fset=set_offset_address_register, fget=get_offset_address_register, notify=cameraInforUpdated5)
