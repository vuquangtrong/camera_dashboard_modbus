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
coils = ModbusSequentialDataBlock(1, [False] * 9999)
discrete_inputs = ModbusSequentialDataBlock(10001, [False] * 9999)
input_registers = ModbusSequentialDataBlock(30001, [0] * 9999)
holding_registers = ModbusSequentialDataBlock(40001, [0] * 9999)

# Define the Modbus slave context
slave_context = ModbusSlaveContext(
    co=coils,
    di=discrete_inputs,
    ir=input_registers,
    hr=holding_registers
)

# Define the Modbus server context
server_context = ModbusServerContext(slaves=slave_context, single=True)

# Start the Modbus TCP server
StartTcpServer(context=server_context, address=("localhost", 5001))
