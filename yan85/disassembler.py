from .machine import Machine, Param, Opcode, Register, Instruction
from enum import Enum
from typing import List
from .utils import *

class Entity:
    class Type(Enum):
        code="CODE"
        byte="BYTE"
    type:Type = Type.byte
    xrefs = []
    line_comment = ""
    plate_comment = ""
    bytes = [0]
    address = 0
    #instruction only parameters
    instruction: Instruction
    params: List[Register|int|None] = [None, None]
    dynamic_branches=False
    branches = []

    def __init__(self, type: Type, address, bytes):
        self.type = type
        self.address = address
        self.bytes = bytes

    def readable(self):
        if self.type == self.Type.byte:
            return self.readable_byte()
        elif self.type == self.Type.code:
            return self.readable_code()

    def readable_byte(self):
        ret = ""
        bytes = ''.join([f'{b:02X} ' for b in self.bytes])
        readable_bytes = ''.join([f'{b:02} ' for b in self.bytes])
        ret += f"{self.address:04X}  {DARK_GRAY}{bytes}{RESET_COLOR} ??    {DARK_GRAY}{readable_bytes}{RESET_COLOR}"
        ret += f"    {DARK_GRAY}{self.line_comment}{RESET_COLOR}"
        return ret

    def readable_code(self):
        """
        generat a readable string of the entity
        """
        opcode = self.instruction.opcode.value
        params_str = ["??", "??"]
        bytes = ''.join([f'{b:02X} ' for b in self.bytes])
        for i in range(len(self.instruction.params)):
            param = self.params[i]
            if isinstance(param, int):
                params_str[i] = hex(param)
            elif isinstance(param, Register):
                params_str[i] = param.value
                if param == Register.N:
                    params_str[i] = f"{DARK_GRAY}N{RESET_COLOR}"



        data = f"{DARK_GRAY}{bytes}{RESET_COLOR} {opcode}   {params_str[0]} {params_str[1]}"
        ret = f"{self.address:04X}  {data}"
        ret += f"    {DARK_GRAY}{self.line_comment}{RESET_COLOR}"
        return ret





class Disassembler:
    # stack of addresses to disassembly
    instr_stack = []
    #a machine that will be used to emulate the code,
    #and infer all the informations required for the static disassembly
    #such as the register name order. It change from machine to machine
    machine: Machine
    # TODO: find the best data type option
    # A copy of the machine memory, where instead of bytes
    # every cell contains a referece to the entity associated to
    # that address
    #vmem_mapping = []
    # an alternative to vmem_mapping: a key-value dict, the key is a memory address,
    # the value is its entity. the entity will contain info about its byte length
    vmem_mapping = {}
    # a dict of entities. An entity can be a byte of data,
    # or a multy byte instruction
    entities = {}


    def __init__(self, machine: Machine):
        self.machine = machine
        self.instr_stack.append(machine.conf['code_base_address'])
        while len(self.instr_stack) > 0:
            #pop an instruction from the stack
            instr_addr = self.instr_stack.pop()
            self.disass_sweep(instr_addr)


    def _byte_at(self, addr):
        return self.machine.vmem[addr]


    def _get_instructionClass(self, opcode_byte)-> Instruction|None:
        if opcode_byte not in self.machine.conf['opcode_bytes']:
            return None
        else:
            opcode = self.machine.conf['opcode_bytes'][opcode_byte]
            instructionClass = self.machine.instructions[opcode]
            return instructionClass

    def _get_register(self, param_byte) -> Register|None:
        if param_byte not in self.machine.conf['register_bytes']:
            return None
        else:
            return self.machine.conf['register_bytes'][param_byte]

    def disass_sweep(self, instr_addr):
        entity = self.disass_instruction(instr_addr)
        print(entity.readable())
        #associate the instruction entity to the current instruction
        self.vmem_mapping[instr_addr] = entity
        # if the entity is an instruction
        if entity.type == Entity.Type.code:
            #add the next instruction to the stack, since this is a linear sweep
            #TODO: do this in a new function
            if instr_addr+3 < len(self.machine.vmem):
                self.instr_stack.append(instr_addr+3)


    def disass_instruction(self, instr_addr) -> Entity:
        instr_bytes = [
            self._byte_at(instr_addr),
            self._byte_at(instr_addr+1),
            self._byte_at(instr_addr+2),
        ]
        # print(f"[DEBUG] disass {hex(instr_addr)}: {hex(instr_bytes[0])} {hex(instr_bytes[1])} {hex(instr_bytes[2])}")

        instruction = self._get_instructionClass(instr_bytes[0])
        disass_error = ""
        instr_entity = Entity(
            Entity.Type.code,
            instr_addr,
            instr_bytes
            )

        if instruction is None:
            # Invalid instruction
            disass_error = "Invalid Opcode"
        else:
            # Disassemble generic instruction
            instr_entity.instruction = instruction
            params_as_reg = [
                self._get_register(instr_bytes[1]),
                self._get_register(instr_bytes[2]),
            ]
            # validate params
            for i in range(len(instruction.params)):
                if instruction.params[i] == Param.reg8:
                    #handle register params
                    if params_as_reg[i] is None:
                        disass_error = f"{instruction.opcode.value} Invalid Register"
                        break
                    else:
                        instr_entity.params[i] = params_as_reg[i]
                elif instruction.params[i] == Param.imm8:
                    #handle data params
                    instr_entity.params[i] = instr_bytes[i]

        #handle instruction comments
        if instr_entity.instruction.opcode == Opcode.STK:
            p1 = instr_entity.params[0]
            p2 = instr_entity.params[1]
            if isinstance(p1, Register) and isinstance(p2, Register):
                if p1 == Register.N and p2 == Register.N:
                    comment = "nop"
                elif p2 == Register.N:
                    comment = f"pop {p1.value}"
                elif p1 == Register.N:
                    comment = f"push {p2.value}"
                else:
                    comment = f"{p1.value} = {p2.value}"
                instr_entity.line_comment = comment
        if instr_entity.instruction.opcode == Opcode.IMM:
            p2 = instr_entity.params[1]
            if isinstance(p2, int) and p2 >= ord(' ') and p2 <= ord('~'):
                instr_entity.line_comment = f"'{chr(p2)}'"


        #handle invalid instructions
        if len(disass_error) > 0:
            byte_entity = Entity(
                    Entity.Type.byte,
                    instr_addr,
                    instr_bytes
                    )
            byte_entity.line_comment = disass_error
            return byte_entity
        else:
            return instr_entity




