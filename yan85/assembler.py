from .machine import Machine, Param, Opcode, Register, Instruction, InstructionByte
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
    EOF = "EOF"
    NEWLINE = "NEWLINE"
    OPCODE = "OPCODE"
    HEX = "HEX"
    REGISTER = "REGISTER"
    SQUARE_OPEN = "SQUARE_OPEN"
    SQUARE_CLOSE = "SQUARE_CLOSE"
    LABEL = "LABEL"
    SYSNAME = "SYSNAME"

class Token:
    def __init__(self, type, value):
        self.type = type
        self.value = value

class UnlinkedInstruction:
    pseudo_instruction = True
    tokens: List[Token]
    bytes: List[int]
    # the labels associated to this instruction
    labels: List[str]
    # {":label_name": bytes_index}
    unresolved_labels: Dict[str, int]


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



        return ""
    
    def parse_register(self, reg_str):
        for k in self.machine.conf_register_bytes:
            if self.machine.conf_register_bytes[k].value == reg_str:
                return k
        raise Exception(f"Cannot convert to bytes register {reg_str}")

    
    def parse_hex(self, hex_str):
        return int(hex_str, 16)

    def parse_instruction(self, tokens, awaiting_labels):
        """
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
        #prepare a readable representation of the current unparsed instruction
        readable = ""
        for t in tokens:
            readable += f"{t.type.value} {t.value}\n"

        # debug print
        print("="*10)
        print(readable)

        #handle label
        if len(tokens) == 1 and tokens[0].type == TokenType.LABEL:
            # add it to the waiting list. it will be attached to the next
            # valid instruction
            awaiting_labels.append(tokens[0].value)
        
        #handle pseudo instructions
        # STK
        # if tokens[0].value == "PUSH":
        #     if 

        # else: 
        #     raise Exception(f"Could not assemble: \n{readable}")
        

        instr = Instruction()
        instr.labels = awaiting_labels[::]
        return instr


