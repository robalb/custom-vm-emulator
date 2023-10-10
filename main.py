from yan85.machine import Machine, Opcode, Register, TrapType
from yan85.disassembler import Disassembler
from yan85.utils import *
from yan85.debugger.core import Debugger

code_dump = """
10 00 00 10 00 00 10 00 00 10 00 00 10 00 00 10 00 00
"""


# initialze a yan85 machine
machine = Machine(
        vmem_bytes = 1080,
        code_base_address = 0,
        registers_base_address = 0x400,
        memory_base_address = 0x300,
        register_bytes = {
            0x0:  Register.N,
            0x10: Register.A,
            0x20: Register.B,
            0x2:  Register.C,
            0x8:  Register.D,
            0x4:  Register.s,
            0x40: Register.i,
            0x1:  Register.f,
            },
        opcode_bytes = {
            0x40: Opcode.IMM,
            0x1:  Opcode.ADD,
            0x10: Opcode.STK,
            0x8:  Opcode.STM,
            0x2:  Opcode.LDM,
            0x20: Opcode.CMP,
            0x4:  Opcode.JMP,
            0x80: Opcode.SYS,
            }
        )

machine.load_code(code_dump)


breaks = [
    0x06,
    ]

comments = {
        0x3: "plate comment()",
        0x9: " inline top comment",
        }

debugger = Debugger(machine, breaks, comments)



#dis = Disassembler(machine)
# print(hexdump(machine.vmem))
