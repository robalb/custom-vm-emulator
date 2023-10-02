from .machine import Machine
from enum import Enum

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

    # CODE only parameters
    opcode = ""
    param1 = ""
    param1_type = ""
    param2 = ""
    param2_type = ""
    dynamic_branches=False
    branches = []

    def __init__(self, type: Type, address, bytes):
        self.type = type
        self.address = address
        self.bytes = bytes



class Disassembler:

    # stack of addresses to disassembly
    instr_stack = []

    #a machine that will be used to emulate the code,
    #and infer all the informations required for the static disassembly
    #such as the register name order. It change from machine to machine
    machine: Machine|None = None

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
            self.disass_instruction(instr_addr)

    def _byte_at(self, addr):
        return self.machine.vmem[addr]

    def disass_instruction(self, instr_addr):
        instr_bytes = [
            self._byte_at(instr_addr),
            self._byte_at(instr_addr+1),
            self._byte_at(instr_addr+2),
        ]
        #TODO: map opcode to name, map params to readable name
        # stop if instruction is invalid.TODO: remove. this is temporary
        if instr_bytes[0] == 0 and instr_bytes[1] == 0:
            return
        print(instr_addr, instr_bytes)

        #create entity associated to the current instruction
        self.vmem_mapping[instr_addr] = Entity(
            Entity.Type.code,
            instr_addr,
            instr_bytes
            )

        #add the next instruction to the stack, since this is a linear sweep
        self.instr_stack.append(instr_addr+3)




