import re
from enum import Enum

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

def tokenize(input_string):
    tokens = []

    # Define regular expressions for each token type
    patterns = [
        (TokenType.NEWLINE, r'(?:\n|#.*\n)+'),
        (TokenType.SYSNAME, r'[a-z][a-z_]+\(\)'),
        (TokenType.OPCODE, r'[A-Z][A-Z_]{2,10}'),
        (TokenType.HEX, r'0x[0-9A-Fa-f]{1,2}'),
        (TokenType.REGISTER, r'[A-Za-z]{1}'),
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

# Example usage
input_string = "ADD R1, [R2], 0x1 :label sysname()"
input_string = """
#comment
:label
ADD A B
PUSH C
SYS read() C
LDM A [i]
IMM a :label
IMM a :label # some text

"""
tokens = tokenize(input_string)
for token in tokens:
    print(f"Type: {token.type.value}")
