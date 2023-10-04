from IPython import embed
from yan85.machine import Machine, Opcode, Register, TrapType
from yan85.disassembler import Disassembler
from yan85.utils import *

code_dump = """
40 40 b1 40 20 01 01 20 04 40 08 49 10 00 08 40
08 4e 10 00 08 40 08 43 10 00 08 40 08 4f 10 00
08 40 08 52 10 00 08 40 08 52 10 00 08 40 08 45
10 00 08 40 08 43 10 00 08 40 08 54 10 00 08 40
08 21 10 00 08 40 08 0a 10 00 08 40 02 0b 40 10
01 80 10 08 40 10 01 80 02 00 10 00 10 10 00 20
10 00 02 40 20 01 01 20 04 40 08 4b 10 00 08 40
08 45 10 00 08 40 08 59 10 00 08 40 08 3a 10 00
08 40 08 20 10 00 08 40 02 05 40 10 01 80 10 08
10 02 00 10 20 00 10 10 00 10 00 10 10 00 20 10
00 02 40 20 30 40 02 08 40 10 00 80 08 08 10 02
00 10 20 00 10 10 00 40 40 ca 40 20 01 01 20 04
40 08 43 10 00 08 40 08 4f 10 00 08 40 08 52 10
00 08 40 08 52 10 00 08 40 08 45 10 00 08 40 08
43 10 00 08 40 08 54 10 00 08 40 08 21 10 00 08
40 08 20 10 00 08 40 08 59 10 00 08 40 08 6f 10
00 08 40 08 75 10 00 08 40 08 72 10 00 08 40 08
20 10 00 08 40 08 66 10 00 08 40 08 6c 10 00 08
40 08 61 10 00 08 40 08 67 10 00 08 40 08 3a 10
00 08 40 08 0a 10 00 08 40 02 14 40 10 01 80 10
08 40 08 2f 40 02 80 08 02 08 40 08 66 40 02 81
08 02 08 40 08 6c 40 02 82 08 02 08 40 08 61 40
02 83 08 02 08 40 08 67 40 02 84 08 02 08 40 08
00 40 02 85 08 02 08 40 10 80 40 20 00 80 20 08
40 20 00 01 20 04 40 02 ff 40 10 00 01 10 08 80
08 08 40 20 00 01 20 04 40 02 00 01 02 08 40 10
01 80 10 08 40 10 00 80 02 00 40 10 30 40 20 a0
40 02 06 40 08 02 01 08 40 10 00 08 40 40 9b 40
02 00 20 08 02 40 08 3e 04 02 08 40 08 01 04 18
08 01 10 02 01 20 02 40 08 ff 01 10 08 01 20 08
10 00 10 10 00 20 02 10 10 02 20 20 20 10 20 10
20 00 10 10 00 40 08 af 04 01 08 40 08 ff 01 02
08 40 08 00 20 02 08 40 08 9d 04 01 08 10 08 02
10 40 00 40 08 b9 40 02 9e 08 02 08 40 08 42 40
02 9f 08 02 08 40 08 b5 40 02 a0 08 02 08 40 08
01 40 02 a1 08 02 08 40 08 dd 40 02 a2 08 02 08
40 08 7b 40 02 a3 08 02 08 40 08 7a 40 02 a4 08
02 08 40 08 ee 40 02 a5 08 02 08 40 40 1e 10 00
10 10 00 20 10 00 02 10 02 00 10 20 00 10 10 00
40 40 8e 00 00 00 00 00 00 00 00 00 00 00 00 00
"""

# initialze a yan85 machine
machine = Machine(
        vmem_bytes = 1080,
        code_base_address = 0,
        registers_base_address = 0x400,
        register_bytes = {
            0x0:  Register.N,
            0x10: Register.A,
            0x20: Register.B,
            0x2:  Register.C,
            0x8:  Register.D,
            0x4:  Register.s,
            0x40: Register.i,
            0x1:  Register.f,
            # 0x0: Register.N,
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

machine.trap_mode_enabled = True
def handler(machine, type):
    if type is not TrapType.trap_mode:
        print(f"some actual error occurred {type}")
    else:
        # print_hexdump(machine.vmem)
        input("yandb$: ")
        machine.run_loop()


# machine.set_trap_handler(handler)
# machine.run_loop()

# embed()
dis = Disassembler(machine)

#yan85 is a simple architecture, and we can emulate it easily.
#therefore we can implement a recursive descent disassembler

#we recreate the yan code executing the challenge, but we just use it to disasseble
# def disass_loop():
#     while true:
#     add8(yan_vmem[ip], 1) #add in module 256
#     disass(yan_vmem, yan_vmem[ip*3])
    
