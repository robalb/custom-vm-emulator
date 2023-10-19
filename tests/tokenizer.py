import re
from enum import Enum

class TokenType(Enum):
    OPCODE="OPCODE" # [A-Z]{0,3}
    HEX="HEX" # 0x[0-9A-Fa-f]{1,2}
    REGISTER="REGISTER" # [A-Za-z]{1}
    SQUARE_OPEN="SQUARE_OPEN" # \[
    SQUARE_CLOSE="SQUARE_CLOSE" # \]
    LABEL="LABEL" # :[A-Za-z0-9]*
    SYSNAME="SYSNAME" # [a-z][a-z]+\(\)

class Token:
    type: TokenType
    value: str
    def __init__(self, type:TokenType, value:str):
        self.type = type
        self.value = value
    
EOF = "\x00"

class Tokenizer:
    # error reporting information
    current_line = 1
    current_row = 0
    error = None

    def __init__(self):
        self.tokens = []
        self.current_token = ""
        self.state = self.__start_state

    def tokenize(self, input_string):
        for i in range(len(input_string)):
            #read current char and ahead char
            char = input_string[i]
            next_char = EOF
            if i+1 < len(input_string):
                next_char = input_string[i+1]
            #update position for error reporting
            self.current_row += 1
            if char == '\n':
                self.current_line += 1
            #advance the tokenizer state machine 1 step
            self.state(char, next_char)
        #TODO: handle unexpected EOF
        # self.flush_token()
        return self.tokens

    def flush_token(self, type: TokenType):
        t = Token(type, self.current_token)
        self.tokens.append(t)
        self.current_token = ""

    def flush_void_token(self):
        self.current_token = ""

    def __start_state(self, char: str, next_char: str):
        # comment
        if char == '#':
            self.state = self.__comment_state
        # space
        if re.match(r'\s', char):
            self.state = self.__space_state
        # register
        elif (re.match(r'[A-Z][a-z]', char) and
              re.match(r'[A-Z][a-z]', next_char) == None):
            self.state = self.__start_state
            self.current_token += char
        elif re.match(r'[a-zA-Z]', char):
            self.state = self.register_state
            self.current_token += char
        elif char.isdigit() or (char == '-' and not self.current_token):
            self.state = self.immediate_state
            self.current_token += char

    def __comment_state(self, char, next_char):
        if (char == '\n' or char == EOF or
            next_char == '\n' or next_char == EOF):
            self.flush_void_token()
            self.state = self.__start_state

    def __space_state(self, char, next_char):
        if (re.match(r'[^\s]', char) or char == EOF or
            re.match(r'[^\s]', next_char) or next_char == EOF):
            self.flush_void_token()
            self.state = self.__start_state

    def opcode_state(self, char):
        if re.match(r'[a-zA-Z]{3}', self.current_token + char):
            self.current_token += char
        else:
            self.flush_token()
            self.state = self.__start_state

    def register_state(self, char):
        if re.match(r'[a-zA-Z]', self.current_token + char):
            self.current_token += char
        else:
            self.flush_token()
            self.state = self.__start_state

    def immediate_state(self, char):
        if re.match(r'^0x[0-9A-Fa-f]+$', self.current_token + char) or \
           re.match(r'^-?\d+$', self.current_token + char):
            self.current_token += char
        else:
            self.flush_token()
            self.state = self.__start_state

    # def flush_token(self):
    #     if self.current_token:
    #         self.tokens.append(self.current_token)
    #         self.current_token = ""

input_string = """
# This is a comment
ADD R1, R2, R3
SUB R4, R5, 0x7F
# Another comment
"""

tokenizer = Tokenizer()
tokenized = tokenizer.tokenize(input_string)
print(tokenized)
