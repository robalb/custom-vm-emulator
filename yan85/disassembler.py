from .machine import Machine, Param, Opcode, Register, Instruction, InstructionByte
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
    changes_flow=False
    branches = []

    def __init__(self, type: Type, address, bytes):
        self.type = type
        self.address = address
        self.bytes = bytes

    def readable(self)-> str:
        if self.type == self.Type.byte:
            return self.readable_byte()
        elif self.type == self.Type.code:
            return self.readable_code()
        else:
            return ""

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

        #highlight CMP instructions
        opcode_color = RESET_COLOR
        if self.instruction.opcode == Opcode.CMP:
            opcode_color = OPCODE_HIGHLIGHT_COLOR

        data = f"{DARK_GRAY}{bytes}{RESET_COLOR} {opcode_color}{opcode}{RESET_COLOR}   {params_str[0]} {params_str[1]}"
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

    comments = {}

    def __init__(self, machine: Machine, comments={}):
        self.comments = comments
        self.machine = machine

    def _byte_at(self, addr):
        return self.machine.vmem[addr]

    def _get_instructionClass(self, opcode_byte)-> Instruction|None:
        if opcode_byte not in self.machine.conf_opcode_bytes:
            return None
        else:
            opcode = self.machine.conf_opcode_bytes[opcode_byte]
            instructionClass = self.machine.instructions[opcode]
            return instructionClass

    def _get_register(self, param_byte) -> Register|None:
        if param_byte not in self.machine.conf_register_bytes:
            return None
        else:
            return self.machine.conf_register_bytes[param_byte]

    def disassemble(self)->str:
        ret = ""
        #reset the disassembler state
        self.instr_stack = []
        self.vmem_mapping = {}
        self.entities = {}
        #disassemble based on the current machine state.
        self.instr_stack.append(self.machine.conf_code_base_address)
        while len(self.instr_stack) > 0:
            #pop an instruction from the stack
            instr_addr = self.instr_stack.pop()
            entity = self.disass_instruction(instr_addr)
            if instr_addr in self.comments:
                comment = self.comments[instr_addr]
                margin = " "*9
                color = ITALIC + COMMENT_COLOR
                if entity.changes_flow:
                    color = ITALIC + FLOW_LINES_COLOR
                if comment[0] == " ":
                    ret += f"{color}{margin}{self.comments[instr_addr][1:]}{RESET_COLOR}\n"
                else:
                    ret += f"{color}{margin}******************************\n{RESET_COLOR}"
                    ret += f"{color}{margin}**  {self.comments[instr_addr]}\n{RESET_COLOR}"
                    ret += f"{color}{margin}******************************\n{RESET_COLOR}"
            ret += self.siderbar_line(entity)
            ret += entity.readable()
            ret += "\n"
            #associate the instruction entity to the current instruction
            # self.vmem_mapping[instr_addr] = entity
            #add the next instruction to the stack
            #if this was not a linear sweep, this should also check that entity.type == code
            if instr_addr+3 < len(self.machine.vmem):
                self.instr_stack.append(instr_addr+3)
        return ret

    def siderbar_line(self, entity)->str:
        instr_addr = self.machine._read_register(Register.i) * 3
        is_current = entity.address == instr_addr

        if is_current:
            is_current = ">>"
        else:
            is_current = "  "
        if entity.changes_flow:
            way = "--"
            runs = f"{FLOW_LINES_COLOR}{way}{RESET_COLOR}"
        else:
            runs = "  "
        return f"   {is_current} {runs} "


    def disass_instruction(self, instr_addr) -> Entity:
        real_instr_bytes = [
            self._byte_at(instr_addr + 0),
            self._byte_at(instr_addr + 1),
            self._byte_at(instr_addr + 2),
        ]
        # normalizes the instruction bytes order, in order to always have
        # instr_bytes[0] <- opcode
        # instr_bytes[1] <- param1
        # instr_bytes[2] <- param2
        bytes_order = self.machine.conf_instruction_bytes_order
        instr_bytes = [
            self._byte_at(instr_addr + bytes_order[InstructionByte.opcode]),
            self._byte_at(instr_addr + bytes_order[InstructionByte.param1]),
            self._byte_at(instr_addr + bytes_order[InstructionByte.param2]),
        ]
        # print(f"[DEBUG] disass {hex(instr_addr)}: {hex(instr_bytes[0])} {hex(instr_bytes[1])} {hex(instr_bytes[2])}")

        instruction = self._get_instructionClass(instr_bytes[0])
        disass_error = ""
        instr_entity = Entity(
            Entity.Type.code,
            instr_addr,
            real_instr_bytes
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
                #handle register params
                if instruction.params[i] == Param.reg8:
                    if params_as_reg[i] is None:
                        disass_error = f"{instruction.opcode.value} Invalid Register"
                        break
                    else:
                        instr_entity.params[i] = params_as_reg[i]
                #handle data params
                elif instruction.params[i] == Param.imm8:
                    instr_entity.params[i] = instr_bytes[i+1]

            #handle instruction comments or special cases
            if instr_entity.instruction.opcode == Opcode.STK:
                p1 = instr_entity.params[0]
                p2 = instr_entity.params[1]
                if isinstance(p1, Register) and isinstance(p2, Register):
                    #generate comment
                    if p1 == Register.N and p2 == Register.N:
                        comment = "nop"
                    elif p2 == Register.N:
                        comment = f"pop {p1.value}"
                    elif p1 == Register.N:
                        comment = f"push {p2.value}"
                    else:
                        comment = f"{p1.value} = {p2.value}"
                    instr_entity.line_comment = comment
                    #check effect on instruction flow
                    if p1 == Register.i or p2 == Register.i:
                        instr_entity.changes_flow = True

            if instr_entity.instruction.opcode == Opcode.IMM:
                p1 = instr_entity.params[0]
                p2 = instr_entity.params[1]
                if isinstance(p1, Register) and isinstance(p2, int):
                    if p1 == Register.i:
                        instr_entity.line_comment = f"JMP {hex(p2*3)}"
                        instr_entity.changes_flow = True
                    elif p2 >= ord(' ') and p2 <= ord('~'):
                        instr_entity.line_comment = f"'{chr(p2)}'"

            if instr_entity.instruction.opcode == Opcode.JMP:
                instr_entity.changes_flow = True
                p1 = instr_entity.params[0]
                if isinstance(p1, int):
                    flags = [f.value for f in self.machine._get_flags(p1)]
                    flags = "".join(flags)
                    instr_entity.line_comment = f" ({flags})"

            if instr_entity.instruction.opcode == Opcode.SYS:
                p1 = instr_entity.params[0]
                if isinstance(p1, int):
                    syscall_bytes = self.machine.conf_syscall_bytes
                    if p1 not in syscall_bytes:
                        disass_error = f"syscall  Invalid number {hex(p1)}"
                    else:
                        syscall = syscall_bytes[p1].value
                        instr_entity.line_comment = f"{syscall}()"

        #handle invalid instructions
        if len(disass_error) > 0:
            byte_entity = Entity(
                    Entity.Type.byte,
                    instr_addr,
                    real_instr_bytes
                    )
            byte_entity.line_comment = disass_error
            return byte_entity
        else:
            return instr_entity




