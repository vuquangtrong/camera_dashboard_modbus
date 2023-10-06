import logging
import threading
from pymodbus.datastore import ModbusSequentialDataBlock, ModbusSlaveContext, ModbusServerContext
from pymodbus.server.async_io import StartTcpServer, ServerStop

# Enable logging (makes it easier to debug if something goes wrong)
logging.basicConfig()
log = logging.getLogger()
log.setLevel(logging.ERROR)


class Modbus_Server:
    def __init__(self) -> None:
        # Define the Modbus registers
        self._coils = ModbusSequentialDataBlock(0, [False] * 9999)
        self._discrete_inputs = ModbusSequentialDataBlock(0, [False] * 9999)
        self._input_registers = ModbusSequentialDataBlock(0, [0] * 9999)
        self._holding_registers = ModbusSequentialDataBlock(0, [0] * 9999)

        # Define the Modbus slave context
        self._slave_context = ModbusSlaveContext(
            co=self._coils,
            di=self._discrete_inputs,
            ir=self._input_registers,
            hr=self._holding_registers,
            # zero_mode = True
        )

        # Define the Modbus server context
        self._server_context = ModbusServerContext(slaves=self._slave_context, single=True)

    def serve(self):
        StartTcpServer(context=self._server_context, address=("localhost", 5001))

    def start(self):
        threading.Thread(target=self.serve, daemon=True).start()

    def stop(self):
        ServerStop()
