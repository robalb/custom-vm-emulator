from .utils import *
from enum import Enum
from typing import List, Callable

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
    s='s' #stack pointer
    i='i' #instructions counter
    f='f' #flags
    N='N' #no register

class Flag(Enum):
    N='N' #r1 != r2
    E='E' #r1 == r2
    Z='Z' #r1 == r2 == 0
    G='G' #r1 > r2
    L='L' #r1 < r2

class Syscall(Enum):
    exit='exit'
    sleep='sleep'
    read_code='read_code'
    read_memory='read_memory'
    open='open'
    write='write'


class TrapType(Enum):
    trap_mode='trap_mode'
    invalid_opcode='invalid_opcode'
    invalid_read='invalid_read'
    invalid_write='invalid_write'
    invalid_register='invalid_register'
    program_exit='program_exit'

class Instruction:
    opcode: Opcode
    params: List[Param]
    description: str

class Machine:
    #machine virtual memory
    vmem = []
    #all the configurations that can change in yan85
    #machine variations
    conf = {
        'vmem_bytes': 0,
        'code_base_address': 0x0,
        'registers_base_address': 0x400,
        'memory_base_address': 0x300,
        #individual offset of each register from registers base address
        'registers_address_offset': {
            Register.A: 0x0,
            Register.B: 0x1,
            Register.C: 0x2,
            Register.D: 0x3,
            Register.s: 0x4,
            Register.i: 0x5,
            Register.f: 0x6,
        },
        'register_bytes': {
            0x0:  Register.N,
            0x1:  Register.A,
            0x2:  Register.B,
            0x4:  Register.C,
            0x8:  Register.D,
            0x10: Register.s,
            0x20: Register.i,
            0x40: Register.f,
        },
        'opcode_bytes': {
            0x0:  Opcode.IMM,
            0x1:  Opcode.ADD,
            0x2:  Opcode.STK,
            0x4:  Opcode.STM,
            0x8:  Opcode.LDM,
            0x10: Opcode.CMP,
            0x20: Opcode.JMP,
            0x40: Opcode.SYS,
            },
        'flag_bytes': {
            0x1:  Flag.N,
            0x2:  Flag.E,
            0x4:  Flag.Z,
            0x8:  Flag.G,
            0x10: Flag.L
            },
        'syscall_bytes': {
            0x20: Syscall.open,
            0x4:  Syscall.read_code,
            0x8:  Syscall.read_memory,
            0x10: Syscall.write,
            0x1:  Syscall.sleep,
            0x2:  Syscall.exit,
            }
        }

    # the machine was halted
    trap_halt = False
    trap_reason: TrapType|None = None
    # when true, set trap every time an instruction runs
    trap_mode_enabled = False
    # this callback is executed every time a trap is reached
    trap_handler: Callable|None = None

    stdin_buffer = b""

    class InstructionIMM(Instruction):
        opcode = Opcode.IMM
        params = [Param.reg8, Param.imm8]
        description = """
        IMM(reg, imm)
            reg = imm

        put the imm byte into reg
        """

    class InstructionADD(Instruction):
        opcode = Opcode.ADD
        params = [Param.reg8, Param.reg8]
        description = """
        ADD(reg1, reg2)
            reg1 = reg1+reg2

        """

    class InstructionSTK(Instruction):
        opcode = Opcode.STK
        params = [Param.reg8, Param.reg8]
        description = """
        STK(reg1, reg2)
          if reg2: push(reg2)
          if reg1: pop(reg1)

          reg1: pop into reg1 if reg1 is not zero
          reg2: push reg2 if reg2 is not zero
          if both are set, this acts as a mov from reg2 into reg1
          Register.s is used as stack pointer:
              incremented before push
              decremented after pop,
        """

    class InstructionSTM(Instruction):
        opcode = Opcode.STM
        params = [Param.reg8, Param.reg8]
        description = """
        STM(reg1, reg2)
            [reg1] = reg2

        Put the content of reg2 into the addr stored in reg1.
        """

    class InstructionLDM(Instruction):
        opcode = Opcode.LDM
        params = [Param.reg8, Param.reg8]
        description = """
        LTM(reg1, reg2)
            reg1 = [reg2]

        put into reg1 the byte pointed by reg2
        """

    class InstructionCMP(Instruction):
        opcode = Opcode.CMP
        params = [Param.reg8, Param.reg8]
        description = """
        CMP(reg1, reg2)
            put into Register.f the result of the
            comparison between reg1 and reg2.

        Flag register content: (bit order may change)
            4 1
        0000000
          |||||
          ||||r1 == r2
          |||r1 != r2
          ||r1 == 0 && r2 == 0
          |r2 < r1
          r1 < r2
        """

    class InstructionJMP(Instruction):
        opcode = Opcode.JMP
        params = [Param.imm8, Param.reg8]
        description = """
        JMP(imm, reg)
          if imm8 == 0 || Register.f & imm8:
            Register.i = [reg]
          
          reg is a register containing the memory location we
          want to jump to.
          imm8 is the bitmask for the flag we want to check.
          the flag is set when we call cmp, and is inside Register.f 
        """

    class InstructionSYS(Instruction):
        opcode = Opcode.SYS
        params = [Param.imm8, Param.reg8]
        description = """
        SYS(imm, reg)
            imm is the opcode, reg is the param
            other registers could be accessed for extra params
            depending on the opcode
        """

    # map every Opcode to an instruction
    instructions = {
            Opcode.IMM: InstructionIMM,
            Opcode.ADD: InstructionADD,
            Opcode.IMM: InstructionIMM,
            Opcode.ADD: InstructionADD,
            Opcode.STK: InstructionSTK,
            Opcode.STM: InstructionSTM,
            Opcode.LDM: InstructionLDM,
            Opcode.CMP: InstructionCMP,
            Opcode.JMP: InstructionJMP,
            Opcode.SYS: InstructionSYS,
            }

    def __init__(self, 
                 vmem_bytes=conf['vmem_bytes'],
                 code_base_address=conf['code_base_address'],
                 registers_base_address=conf['registers_base_address'],
                 memory_base_address=conf['memory_base_address'],
                 register_bytes=conf['register_bytes'],
                 opcode_bytes=conf['opcode_bytes'],
                 stdin_buffer=stdin_buffer,
                 ):
        self.conf['vmem_bytes'] = vmem_bytes
        self.conf['code_base_address'] = code_base_address
        self.conf['registers_base_address'] = registers_base_address
        self.conf['memory_base_address'] = memory_base_address
        self.conf['register_bytes'] = register_bytes
        self.conf['opcode_bytes'] = opcode_bytes
        #initialize the virtual memory
        self.reset_memory()
        self.stdin_buffer = stdin_buffer


    def reset_memory(self):
        """
        Set every byte in the virtual memory to zero
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


    def run_loop(self):
        self.trap_halt = False
        self.trap_type = None

        while not self.trap_halt:
            #fetch instruction bytes
            pc = self._read_register(Register.i)
            instr_addr = pc * 3
            opcode = self._read_vmem(instr_addr)
            param1 = self._read_vmem(instr_addr+1)
            param2 = self._read_vmem(instr_addr+2)
            #increment program counter
            self._write_register(Register.i, pc+1)
            #execute fetched instruction
            self.run_instruction(opcode, param1, param2)
        self.handle_trap()


    def handle_trap(self):
        print(f"[DEBUG] Machine Halted! - {str(self.trap_type)}")
        if self.trap_handler is not None:
            self.trap_handler(self, self.trap_type)
        else:
            print("[DEBUG] Execution stopped. No trap handler is set.")


    def set_trap_handler(self, handler: Callable|None):
        """
        set a callback function that will run when a trap is reached.
        Set to None to remove.
        """
        self.trap_handler = handler


    def run_instruction(self, opcode_byte, param1_byte, param2_byte):
        """
        This methid takes 3 bytes and interprets them as a yan85 instruction
        Note: ian85 has fixed-size, 3 bytes instructions.
        """
        opcodes = self.conf['opcode_bytes']

        print(f"[DEBUG] running: {hex(opcode_byte)} {hex(param1_byte)} {hex(param2_byte)} ")

        # if machine is in trap mode, set trap regardless of
        # the instruction that just run
        if self.trap_mode_enabled:
            self._set_trap(TrapType.trap_mode)

        #invalid opcode, set trap
        if opcode_byte not in opcodes:
            self._set_trap(TrapType.invalid_opcode)

        elif opcodes[opcode_byte] == Opcode.IMM:
            print("[DEBUG] IMM")
            self._write_register(
                    self._get_register(param1_byte),
                    param2_byte
                    )

        elif opcodes[opcode_byte] == Opcode.ADD:
            print("[DEBUG] ADD")
            reg1 = self._get_register(param1_byte)
            reg2 = self._get_register(param2_byte)
            self._write_register(
                    reg1,
                    self._read_register(reg1) +
                    self._read_register(reg2)
                    )

        elif opcodes[opcode_byte] == Opcode.STK:
            print("[DEBUG] STK")
            #push
            if param2_byte != 0:
                reg2 = self._get_register(param2_byte)
                #increment stack pointer (stack is not backwards)
                stack_pointer = self._read_register(Register.s)
                stack_pointer += 1
                self._write_register(Register.s, stack_pointer)
                #write to stack
                self._write_memory(
                        stack_pointer,
                        self._read_register(reg2)
                        )
            #pop
            if param1_byte != 0:
                #read from stack
                reg1 = self._get_register(param1_byte)
                stack_pointer = self._read_register(Register.s)
                self._write_register(
                    reg1,
                    self._read_memory(stack_pointer)
                    )
                #decrement stack pointer (stack is not backwards)
                self._write_register(Register.s, stack_pointer-1)

        elif opcodes[opcode_byte] == Opcode.STM:
            print("[DEBUG] STM")
            reg1 = self._get_register(param1_byte)
            reg2 = self._get_register(param2_byte)
            self._write_memory(
                    self._read_register(reg1),
                    self._read_register(reg2),
                    )

        elif opcodes[opcode_byte] == Opcode.LDM:
            print("[DEBUG] LDM")
            reg1 = self._get_register(param1_byte)
            reg2 = self._get_register(param2_byte)
            self._write_register(
                    reg1,
                    self._read_memory(
                        self._read_register(reg2)
                        )
                    )

        elif opcodes[opcode_byte] == Opcode.CMP:
            print("[DEBUG] CMP")
            flag_to_byte = {v: k for k, v in self.conf['flag_bytes'].items()}
            ret= 0
            reg1 = self._get_register(param1_byte)
            reg2 = self._get_register(param2_byte)
            reg1_byte = self._read_register(reg1)
            reg2_byte = self._read_register(reg2)
            # less
            if reg1_byte < reg2_byte:
                ret |= flag_to_byte[Flag.L]
            # greater
            if reg2_byte < reg1_byte:
                ret |= flag_to_byte[Flag.G]
            # equal
            if reg2_byte == reg1_byte:
                ret |= flag_to_byte[Flag.E]
            # not equal
            else:
                ret |= flag_to_byte[Flag.N]
            # zero
            if reg1_byte == 0 and reg2_byte == 0:
                ret |= flag_to_byte[Flag.Z]
            #save result to flags register
            self._write_register(Register.f, ret)

        elif opcodes[opcode_byte] == Opcode.JMP:
            print("[DEBUG] JMP")
            flag_byte = self._read_register(Register.f)
            if param1_byte == 0 or flag_byte & param1_byte != 0:
                # taken
                self._write_register(
                        Register.i,
                        self._read_register(self._get_register(param2_byte))
                        )

        elif opcodes[opcode_byte] == Opcode.SYS:
            print("[DEBUG] SYS")
            if param1_byte in self.conf['syscall_bytes']:
                syscall = self.conf['syscall_bytes'][param1_byte]
                reg = self._get_register(param2_byte)
                if syscall == Syscall.exit:
                    self._syscall_exit()
                if syscall == Syscall.sleep:
                    self._syscall_sleep()
                if syscall == Syscall.read_code:
                    self._syscall_read_code(reg)
                if syscall == Syscall.read_memory:
                    self._syscall_read_memory(reg)
                if syscall == Syscall.open:
                    self._syscall_open()
                if syscall == Syscall.write:
                    self._syscall_write()


    def _syscall_exit(self):
        self._set_trap(TrapType.program_exit)

    def _syscall_read_memory(self, reg: Register):
        """
          read from filedescriptor C bytes into memory
          read(
            fd    = regA (0x100)
            &buff = regB (0x101) + memory_offset
            size  = regC (0x102)
          )
          reg2 = num of bytes read
        """
        stdin_buffer = self.stdin_buffer
        fd = self._read_register(Register.A)
        write_address = self._read_register(Register.B)
        bytes = self._read_register(Register.C)
        read = 0
        for i in range(bytes):
            if i >= len(stdin_buffer):
                return
            read += 1
            byte = stdin_buffer[i]
            self._write_memory(write_address+i, byte)
        self._write_register(reg, read)
        
    def _syscall_read_code(self, reg: Register):
        pass
    def _syscall_write_code(self):
        pass
    def _syscall_open(self):
        pass
    def _syscall_write(self):
        pass
    def _syscall_sleep(self):
        pass


    def _set_trap(self, type: TrapType):
        self.trap_halt = True
        self.trap_type = type


    def _byte(self, data:int):
        """
        we are using python Int to simulate c uint8_t,
        wich off course will have completely different math.
        We fix it by wrapping every math operation with this modulo.
        This is easier than using ctypes
        """
        return data % 256


    def _get_flags(self, flag_byte) -> List[Flag]:
        ret = []
        for flag in self.conf['flag_bytes']:
            if flag_byte & flag:
                ret.append(self.conf['flag_bytes'][flag])
        return ret


    def _get_register(self, byte: int) -> Register:
        """
        Return The Register associated to an instruction byte.
        the byte associated to a register changes with every machine variation.

        If the given byte is not a register,
        Register.A is returned and the trap bit is set
        """
        if byte in self.conf['register_bytes']:
            return self.conf['register_bytes'][byte]
        else:
            self._set_trap(TrapType.invalid_register)
            return Register.A



    def _write_vmem(self, addr: int, data: int):
        """
        Write a single byte to the virtual memory, without adding any offset

        If the given addr is invalid, 
        nothing is written and the trap bit is set
        """
        # addr += self.conf['memory_base_address']
        if addr >= len(self.vmem):
            print(f"[DEBUG] invalid address write: {hex(addr)}")
            self._set_trap(TrapType.invalid_write)
        else:
            self.vmem[addr] = self._byte(data)


    def _read_vmem(self, addr: int):
        """
        Read a single byte from the virtual memory, without adding any offset

        If the given addr is invalid, 
        0 is returned and the trap bit is set.
        """
        if addr >= len(self.vmem):
            print(f"[DEBUG] invalid address read: {hex(addr)}")
            self._set_trap(TrapType.invalid_read)
            return 0
        else:
            return self.vmem[addr]


    def _write_register(self, reg: Register, data: int):
        address = self.conf['registers_base_address']
        address += self.conf['registers_address_offset'][reg]
        self._write_vmem(address, data)


    def _read_register(self, reg: Register):
        address = self.conf['registers_base_address']
        address += self.conf['registers_address_offset'][reg]
        return self._read_vmem(address)


    def _write_memory(self, addr: int, data: int):
        """
        Write a single byte to the memory segment
        (addr + memory_base_address)
        """
        addr += self.conf['memory_base_address']
        self._write_vmem(addr, data)


    def _read_memory(self, addr: int):
        """
        Read a single byte from the memory segment
        (addr + memory_base_address)
        """
        addr += self.conf['memory_base_address']
        return self._read_vmem(addr)

