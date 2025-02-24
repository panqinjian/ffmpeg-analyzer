from typing import Dict
import os
import sys
import re
from enum import Enum

from core.error_types import FFmpegError, ErrorLevel

class FilterTokenType(Enum):
    IDENTIFIER = 1
    EQUAL = 2
    COMMA = 3
    SEMICOLON = 4
    LBRACKET = 5
    RBRACKET = 6
    NUMBER = 7
    STRING = 8
    EXPRESSION = 9
    PATH = 10
    COLON = 12
    BACKSLASH = 13
    ASTERISK = 14
    OPTION = 15
    FILTER = 16
    EOF = 11

class FilterLexer:
    _patterns = [
        (r'\[', FilterTokenType.LBRACKET),
        (r'\]', FilterTokenType.RBRACKET),
        (r';', FilterTokenType.SEMICOLON),
        (r'=', FilterTokenType.EQUAL),
        (r',', FilterTokenType.COMMA),
        (r':', FilterTokenType.COLON),
        r'(?P<string>"(?:[^"\\]|\\.)*")',
        (r'(?P<number>-?\d+\.?\d*)', FilterTokenType.NUMBER),
        # 允许单个字母（如 v/a/s）和复杂表达式
        (r'(?P<expr>[a-zA-Z0-9_/:\.\+\-]+)', FilterTokenType.EXPRESSION),  
        (r'\s+', None)
    ]

    def __init__(self, text: str):
        self.text = text
        self.pos = 0

    def tokenize(self):
        if not self.text:
            return [(FilterTokenType.EOF, "")]
        tokens = []
        token_type = None
        compiled_patterns = [
            (re.compile(pattern[0]), token_type) if isinstance(pattern, tuple) else 
            (re.compile(pattern), None)
            for pattern in self._patterns
        ]

        while self.pos < len(self.text):
            match_found = False
            for regex, token_type in compiled_patterns:
                match = regex.match(self.text, self.pos)
                if match:
                    match_found = True
                    groups = match.groupdict()
                    if 'string' in groups and groups['string']:
                        value = groups['string'][1:-1].replace('\\"', '"')
                        tokens.append((FilterTokenType.STRING, value))
                    elif 'number' in groups and groups['number']:
                        tokens.append((FilterTokenType.NUMBER, float(groups['number'])))
                    elif 'expr' in groups and groups['expr']:
                        tokens.append((FilterTokenType.EXPRESSION, groups['expr']))
                    else:
                        tokens.append((token_type, match.group()))
                    self.pos = match.end()
                    break
            if not match_found:
                raise FFmpegError(
                    code="LEXER_ERROR",
                    message=f"无法识别的字符: {self.text[self.pos]}",
                    suggestion=f"请检查'{self.text[self.pos]}'附近的语法，确保使用了正确的FFmpeg选项和滤镜参数",
                    level=ErrorLevel.CRITICAL
                )

        tokens.append((FilterTokenType.EOF, ""))
        return tokens