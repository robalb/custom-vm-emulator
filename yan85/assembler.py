from .machine import Machine, Param, Opcode, Register, Instruction, InstructionByte, Flag
from enum import Enum
from typing import List, Dict
from .utils import *
import re


language_specs = """
ADD   A B

CMP   i D

SYS 0x2 D
    # SYS pseudo instructions
    SYS write() D

IMM   B 0x0
    # IMM pseudo instructions
    # :label addr. must be resolved, and divided by 3
    IMM  A  :label

JMP   0x2 D
    # JMP pseudo instructions
    # syntax: J_(Z)(E|N)(G|L)
    J_NLZ D
    J_GZ  D

STK   A B
    # STK pseudo instructions
    NOP
    PUSH  A
    POP   A

LDM   B [B]  <- brackets are optional
                acts as visual help.
                you cannot put them in the wrog order, syntax error
                LDM [B] B , LDM [B] [B]  << error
STM   [A] A
"""

example = """
IMM A 0
IMM i :loop
:loop_body

PUSH A
PUSH B
PUSH C
IMM A 0x0
IMM B 0x30
ADD B 
IMM C 0x2
SYS read() D
POP C
POP B
POP A

IMM B 0x1
ADD A B
:loop
IMM C 0x5
CMP A C
IMM D :loop_body
J_L D

"""


class TokenType(Enum):
    EOF          = "_EOF"
    NEWLINE      = "_NEWLINE"
    HEX          = "_HEX"
    REGISTER     = "_REGISTER"
    LABEL        = "_LABEL"
    SYSNAME      = "_SYSNAME"
    OPCODE       = "_OPCODE"
    SQUARE_OPEN  = "["
    SQUARE_CLOSE = "]"

class Token:
    def __init__(self, type, value):
        self.type = type
        self.value = value

class UnlinkedInstruction:
    tokens: List[Token] = []
    bytes: List[int] = []
    # the labels associated to this instruction
    labels: List[str] = []
    # {":label_name": bytes_index}
    unresolved_labels: Dict[str, int] = {}


def tokenize(input_string) -> List[Token]:
    tokens = []

    # Define regular expressions for each token type
    patterns = [
        (TokenType.NEWLINE, r'(?:\n|#.*\n)+'),
        (TokenType.SYSNAME, r'[a-z][a-z_]+\(\)'),
        (TokenType.OPCODE, r'[A-Z][A-Z_]{2,10}'),
        (TokenType.HEX, r'0x[0-9A-Fa-f]{1,2}'),
        (TokenType.REGISTER, r'[A-DNsif]{1}'),
        (TokenType.SQUARE_OPEN, r'\['),
        (TokenType.SQUARE_CLOSE, r'\]'),
        (TokenType.LABEL, r':[A-Za-z0-9]*'),
    ]

    combined_pattern = '|'.join(f'(?P<{type.name}>{pattern})' for type, pattern in patterns)
    regex = re.compile(combined_pattern)

    # Find all matches in the input string
    for match in regex.finditer(input_string):
        for token_type, token_pattern in patterns:
            token_value = match.group(token_type.name)
            if token_value:
                tokens.append(Token(token_type, token_value))
                break

    # add eof token at the end
    tokens.append(Token(TokenType.EOF, ""))
    return tokens

class Assembler:
    #a machine that will be used to infer all the 
    # informations required for the byte assembly,
    #such as the register name order. It changes from machine to machine
    machine: Machine

    def __init__(self, machine: Machine):
        self.machine = machine

    def assemble(self, code: str):
        # transform the input string into a list of tokens
        tokens = tokenize(code)
        # debug print the tokens
        for t in tokens:
            value = t.value
            if t.type == TokenType.NEWLINE:
                value = ""
            print(t.type.value, value)

        # parse all the tokens between a newline into an instruction
        instructions = []
        awaiting_labels = []
        current_instruction_tokens = []
        for i in range(len(tokens)):
            if tokens[i].type in (TokenType.NEWLINE, TokenType.EOF):
                if len(current_instruction_tokens) > 0:
                    res = self.parse_instruction(current_instruction_tokens, awaiting_labels)
                    instructions.append(res)
                    current_instruction_tokens = []
            else:
                current_instruction_tokens.append(tokens[i])

        print(instructions)



        return ""
    
    def register_to_byte(self, reg_str: str) -> int:
        for k in self.machine.conf_register_bytes:
            if self.machine.conf_register_bytes[k].value == reg_str:
                return k
        raise Exception(f"Cannot convert to bytes register {reg_str}")

    def opcode_to_byte(self, op_str: str) -> int:
        for k in self.machine.conf_opcode_bytes:
            if self.machine.conf_opcode_bytes[k].value == op_str:
                return k
        raise Exception(f"Cannot convert to bytes register {op_str}")

    def hex_to_byte(self, hex_str):
        return int(hex_str, 16)

    def pseudo_JMP_to_byte(self, jmp_str):
        prefix ="J_"
        if not jmp_str.startswith(prefix):
            raise Exception("invalid pseudo JMP")

        flags = jmp_str[len(prefix):]
        ret = 0
        for f in flags:
            found = False
            for k in self.machine.conf_flag_bytes:
                if self.machine.conf_flag_bytes[k].value == f:
                    found = True
                    ret |= k
            if not found:
                raise Exception(f"invalid pseudo JMP Flaf: {f}")
        return ret

    def sysname_to_byte(self, str):
        if not str.endswith("()"):
                raise Exception(f"Invalid sysname: {str}")
        for k in self.machine.conf_syscall_bytes:
            if self.machine.conf_syscall_bytes[k].value == str[:-2]:
                return k
        raise Exception(f"Cannot convert to bytes syscall {str}")


    def parse_instruction(self, tokens: List[Token], awaiting_labels):
        """
        todo: doc
        """

        #prepare a readable representation of the current unparsed instruction
        readable = ""
        for t in tokens:
            readable += f"{t.type.value} {t.value}\n"
        base_error_message = f"Could not assemble: \n{readable}\n"

        # debug print
        print("="*10)
        print(readable)
        
        #prepare the instruction entity
        instr = UnlinkedInstruction()
        
        #handle label
        if len(tokens) == 1 and tokens[0].type == TokenType.LABEL:
            # add it to the waiting list. it will be attached to the next
            # valid instruction
            awaiting_labels.append(tokens[0].value)
            return

        # pseudo instruction
        # PUSH Reg = STK N Reg
        if tokens[0].value == "PUSH":
            if len(tokens) != 2:
                raise Exception(f"{base_error_message} invalid arguments count")
            instr.bytes.append(self.opcode_to_byte(Opcode.STK.value))
            instr.bytes.append(self.register_to_byte(Register.N.value))
            instr.bytes.append(self.register_to_byte(tokens[1].value))

        # pseudo instruction
        # POP Reg = STK Reg N
        elif tokens[0].value == "POP":
            if len(tokens) != 2:
                raise Exception(f"{base_error_message} invalid arguments count")
            instr.bytes.append(self.opcode_to_byte(Opcode.STK.value))
            instr.bytes.append(self.register_to_byte(tokens[1].value))
            instr.bytes.append(self.register_to_byte(Register.N.value))

        # pseudo instruction
        # NOP = STK N N
        elif tokens[0].value == "NOP":
            if len(tokens) != 1:
                raise Exception(f"{base_error_message} invalid arguments count")
            instr.bytes.append(self.opcode_to_byte(Opcode.STK.value))
            instr.bytes.append(self.register_to_byte(Register.N.value))
            instr.bytes.append(self.register_to_byte(Register.N.value))

        # pseudo instruction
        # J_{flags} Reg = JMP {flags} Reg
        elif tokens[0].value.startswith("J_"):
            if len(tokens) != 2:
                raise Exception(f"{base_error_message} invalid arguments count")
            instr.bytes.append(self.opcode_to_byte(Opcode.JMP.value))
            instr.bytes.append(self.pseudo_JMP_to_byte(tokens[0].value))
            instr.bytes.append(self.register_to_byte(tokens[1].value))

        # pseudo instruction
        # decorated STM with square brackets
        # STM [A] B
        elif tokens[0].value == Opcode.STM.value and len(tokens) == 5:
            if (tokens[1].type == TokenType.SQUARE_OPEN and
                tokens[3].type == TokenType.SQUARE_CLOSE):
                instr.bytes.append(self.opcode_to_byte(tokens[0].value))
                instr.bytes.append(self.register_to_byte(tokens[2].value))
                instr.bytes.append(self.register_to_byte(tokens[4].value))
            elif (tokens[2].type == TokenType.SQUARE_OPEN and
                tokens[4].type == TokenType.SQUARE_CLOSE):
                raise Exception(f"{base_error_message} decorations errror: squares on wrong register ")
            else:
                raise Exception(f"{base_error_message} invalid arguments count")

        # pseudo instruction
        # decorated LDM with square brackets
        # STM A [B]
        elif tokens[0].value == Opcode.LDM.value and len(tokens) == 5:
            if (tokens[2].type == TokenType.SQUARE_OPEN and
                tokens[4].type == TokenType.SQUARE_CLOSE):
                instr.bytes.append(self.opcode_to_byte(tokens[0].value))
                instr.bytes.append(self.register_to_byte(tokens[1].value))
                instr.bytes.append(self.register_to_byte(tokens[3].value))
            elif (tokens[1].type == TokenType.SQUARE_OPEN and
                tokens[3].type == TokenType.SQUARE_CLOSE):
                raise Exception(f"{base_error_message} decorations errror: squares on wrong register ")
            else:
                raise Exception(f"{base_error_message} LDM invalid arguments count")

        # pseudo instruction
        # imm with string label
        # IMM A :label
        elif (tokens[0].value == Opcode.IMM.value and
              len(tokens) == 3 and
              tokens[2].type == TokenType.LABEL):
            instr.bytes.append(self.opcode_to_byte(tokens[0].value))
            instr.bytes.append(self.register_to_byte(tokens[1].value))
            # the instr byte at index 2 temporarily set to 0.
            # we associate that byte index to the unresolved label name
            instr.bytes.append(0)
            instr.unresolved_labels[tokens[2].value] = 2

        # pseudo instruction
        # sys with readable function name
        # SYS read() D
        elif (tokens[0].value == Opcode.SYS.value and
              len(tokens) == 3 and
              tokens[1].type == TokenType.SYSNAME):
            instr.bytes.append(self.opcode_to_byte(tokens[0].value))
            instr.bytes.append(self.sysname_to_byte(tokens[1].value))
            instr.bytes.append(self.register_to_byte(tokens[2].value))

        # handle the rest of the instructions here, using the
        # Instruction class in the machine for basic syntax checking
        else:
            #get the opcode Instruction info class
            instr_definition = None
            for k in self.machine.instructions:
                if k.value == tokens[0].value:
                    instr_definition = self.machine.instructions[k]
            if instr_definition is None:
                raise Exception(f"{base_error_message} cannot find instruction definition")
            
            # get the opcode byte
            instr.bytes.append(self.opcode_to_byte(tokens[0].value))

            # validate arguments count
            if len(tokens)-1 != len(instr_definition.params):
                raise Exception(f"{base_error_message} expected {len(instr_definition.params)} parameters, got {len(tokens)-1}")

            #get the rest of the parameters
            i = 0
            for param in instr_definition.params:
                i += 1
                if param == Param.imm8:
                    instr.bytes.append(self.hex_to_byte(tokens[i].value))
                if param == Param.reg8:
                    instr.bytes.append(self.register_to_byte(tokens[i].value))
        

        # if there are labels, add them to the instruction, then remove the list
        instr.labels = awaiting_labels[::]
        awaiting_labels = []
        instr.tokens = tokens[::]
        print("---")
        print("instruction:")
        print(instr.bytes, instr.labels, instr.unresolved_labels, instr.tokens)
        return instr


