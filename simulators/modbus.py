"""
Simulate Modbus server
"""

import logging
from pymodbus.datastore import ModbusSequentialDataBlock, ModbusSlaveContext, ModbusServerContext
from pymodbus.server.async_io import StartTcpServer

# Enable logging (makes it easier to debug if something goes wrong)
logging.basicConfig()
log = logging.getLogger()
log.setLevel(logging.DEBUG)

# Define the Modbus registers
coils = ModbusSequentialDataBlock(1, [False] * 10)
discrete_inputs = ModbusSequentialDataBlock(1, [False] * 10)
holding_registers = ModbusSequentialDataBlock(1, [0] * 10)
input_registers = ModbusSequentialDataBlock(1, [0] * 10)

# Define the Modbus slave context
slave_context = ModbusSlaveContext(
    di=discrete_inputs,
    co=coils,
    hr=holding_registers,
    ir=input_registers
)

# Define the Modbus server context
server_context = ModbusServerContext(slaves=slave_context, single=True)

# Start the Modbus TCP server
StartTcpServer(context=server_context, address=("localhost", 5001))
