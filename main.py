from yan85.machine import Machine, Opcode, Register, TrapType
from yan85.disassembler import Disassembler
from yan85.utils import *
from yan85.debugger.core import Debugger

code_dump = """
10 00 00 10 00 00 10 00 00 10 00 00 10 00 00 10 00 00
"""


# define a yan85 machine with custom variations
class Machine_test(Machine):
    conf_vmem_bytes = 1080
    conf_code_base_address = 0
    conf_registers_base_address = 0x400
    conf_memory_base_address = 0x300
    conf_register_bytes = {
        0x0:  Register.N,
        0x10: Register.A,
        0x20: Register.B,
        0x2:  Register.C,
        0x8:  Register.D,
        0x4:  Register.s,
        0x40: Register.i,
        0x1:  Register.f,
        }
    conf_opcode_bytes = {
        0x40: Opcode.IMM,
        0x1:  Opcode.ADD,
        0x10: Opcode.STK,
        0x8:  Opcode.STM,
        0x2:  Opcode.LDM,
        0x20: Opcode.CMP,
        0x4:  Opcode.JMP,
        0x80: Opcode.SYS,
        }

machine = Machine_test()
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
