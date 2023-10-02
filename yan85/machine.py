from .utils import *
from enum import Enum
from typing import List, Callable
from abc import ABC, abstractmethod

class Opcode(Enum):
    IMM="IMM"
    ADD="ADD"
    STK="STK"
    STM="STM"
    LDM="LDM"
    CMP="CMP"
    JMP="JMP"
    SYS="SYS"

class Param(Enum):
    reg8="reg8"
    imm8="imm8"

class Register(Enum):
    A='A'
    B='B'
    C='C'
    D='D'
    s='s'
    i='i' #instructions counter
    f='f'

class Instruction:
    opcode: Opcode
    params: List[Param]
    description: str
    # @abstractmethod
    # def run(self):
    #     pass

class Machine:
    #machine virtual memory
    vmem = []
    #all the configuration that changes in every yan85
    #machine variation
    conf = {
        'vmem_bytes': 0,
        'code_base_address': 0x0,
        'registers_base_address': 0x400,
        #individual offset of each register from registers base address
        'A_address': 0x0,
        'B_address': 0x1,
        'C_address': 0x2,
        'D_address': 0x3,
        's_address': 0x4,
        'i_address': 0x5,
        'f_address': 0x6,
        'register_bytes': {
            0x0: Register.A,
            0x1: Register.B,
            0x2: Register.C,
            0x3: Register.D,
            0x4: Register.s,
            0x5: Register.i,
            0x5: Register.f,
            },
        'opcode_bytes': {
            0x0: Opcode.IMM,
            0x1: Opcode.ADD,
            0x2: Opcode.STK,
            0x3: Opcode.STM,
            0x4: Opcode.LDM,
            0x5: Opcode.CMP,
            0x6: Opcode.JMP,
            0x7: Opcode.SYS,
            }
        }
    # the machine was halted
    trap_halt = False

    class InstructionIMM(Instruction):
        opcode = Opcode.IMM
        params = [Param.reg8, Param.reg8]
        description = "some description"

    class InstructionADD(Instruction):
        opcode = Opcode.ADD
        params = [Param.reg8, Param.reg8]
        description = "some description"

    # map every Opcode to an instruction
    instructions = {
            Opcode.IMM: InstructionIMM,
            Opcode.ADD: InstructionADD
            }

    def __init__(self, 
                 vmem_bytes=conf['vmem_bytes'],
                 code_base_address=conf['code_base_address'],
                 registers_base_address=conf['registers_base_address'],
                 register_bytes=conf['register_bytes'],
                 opcode_bytes=conf['opcode_bytes']
                 ):
        self.conf['vmem_bytes'] = vmem_bytes
        self.conf['code_base_address'] = code_base_address
        self.conf['registers_base_address'] = registers_base_address
        self.conf['register_bytes'] = register_bytes
        self.conf['opcode_bytes'] = opcode_bytes
        #initialize the virtual memory
        self.reset_memory()


    def reset_memory(self):
        """
        Set every byte int the virtual memory to zero
        """
        self.vmem = [0] * self.conf['vmem_bytes']


    def load_code(self, code_dump: str):
        """
        load yan code into memory, from a hexdump string.
        The code is loaded at offset conf.code_base_address
        The code must be a string containing hex in the format:
            'hh hh hh hh hh hh hh ...'
        """
        code_bytes = []
        dump_to_code_bytes(code_dump, code_bytes)
        virtual_mmap(self.vmem, code_bytes, self.conf['code_base_address'])


    def halt(self, message, opcode_byte, param1_byte, param2_byte):
        print(f"Machine Halted! - {message}")
        print(f"{opcode_byte} {param1_byte} {param2_byte}")
        self.trap_halt = True

    def run_instruction(self, opcode_byte, param1_byte, param2_byte):
        """
        This methid takes 3 bytes and interprets them as a yan85 instruction
        Note: ian85 has fixed-size, 3 bytes instructions.
        """

        opcodes = self.conf['opcode_bytes']
        if opcode_byte not in opcodes:
            self.halt("invalid opcode", opcode_byte, param1_byte, param2_byte)
            return

        if opcodes[opcode_byte] == Opcode.IMM:
            pass
        if opcodes[opcode_byte] == Opcode.ADD:
            pass


