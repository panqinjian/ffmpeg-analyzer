import re
from enum import Enum

class GlobalTokenType(Enum):
    INPUT = "-i"
    THREADS = "-threads"
    HWACCEL = "-hwaccel"
    FILTER_COMPLEX = "-filter_complex"
    MAP = "-map"
    CODEC = "-c"
    STRING = "STRING"
    NUMBER = "NUMBER"
    EQUAL = "="
    EOF = "EOF"

class GlobalCommandLexer:
    def __init__(self, command: str):
        self.command = command
        self.pos = 0
        self.tokens = []
        
    def tokenize(self):
        patterns = [
            (r'-i\b', GlobalTokenType.INPUT),
            (r'-threads\b', GlobalTokenType.THREADS),
            (r'-hwaccel\b', GlobalTokenType.HWACCEL),
            (r'-filter_complex\b', GlobalTokenType.FILTER_COMPLEX),
            (r'-map\b', GlobalTokenType.MAP),
            (r'-c:[va]\b', GlobalTokenType.CODEC),
            (r'"([^"]*)"', GlobalTokenType.STRING),
            (r'\d+', GlobalTokenType.NUMBER),
            (r'=', GlobalTokenType.EQUAL),
            (r'\s+', None)
        ]
        
        while self.pos < len(self.command):
            for pattern, tok_type in patterns:
                regex = re.compile(pattern)
                match = regex.match(self.command, self.pos)
                if match:
                    if tok_type:
                        value = match.group(1) if tok_type == GlobalTokenType.STRING else match.group()
                        self.tokens.append({"type": tok_type, "value": value})
                    self.pos = match.end()
                    break
            else:
                raise ValueError(f"无法解析的字符: {self.command[self.pos]}")
        
        self.tokens.append({"type": GlobalTokenType.EOF, "value": ""})
        return self.tokens