import re
from enum import Enum
import os
import sys

class_path = os.path.join(os.getcwd(), "custom_nodes","ffmpeg-analyzer")
sys.path.append(class_path)
from __init__ import ClassImporter 
importer = ClassImporter()
importer.class_import(["error_types.py"])
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
        (r'\\', FilterTokenType.BACKSLASH),
        (r'\*', FilterTokenType.ASTERISK),
        r'(?P<string>"(?:[^"\\]|\\.)*")',  # 带转义字符的字符串
        (r'(?P<number>-?\d+\.?\d*)', FilterTokenType.NUMBER),
        (r'(?P<path>[a-zA-Z]:\\(?:[^<>:"/\\|?*\x00-\x1F]+\\)*[^<>:"/\\|?*\x00-\x1F]*)', FilterTokenType.PATH),
        (r'(?P<expr>(-?[a-zA-Z_][\w\.\+\-\*/:]*))', FilterTokenType.EXPRESSION),
        (r'-\w+', FilterTokenType.OPTION),
        (r'(scale|rotate|colorbalance|gblur|eq|colorchannelmixer|volume|amix|hstack)', FilterTokenType.FILTER),
        (r'\s+', None)
    ]

    def __init__(self, text: str):
        self.text = text
        self.pos = 0

    def tokenize(self):
        tokens = []
        token_type = None
        compiled_patterns = [
            (re.compile(pattern[0]), token_type) if isinstance(pattern, tuple) else 
            (re.compile(pattern), None)
            for pattern in self._patterns
        ]

        while self.pos < len(self.text):
            print(f"当前字符: {self.text[self.pos]}")
            for regex, token_type in compiled_patterns:
                match = regex.match(self.text, self.pos)
                if match:
                    if token_type:
                        groups = match.groupdict()
                        if 'string' in groups and groups['string']:
                            value = groups['string'][1:-1].replace('\\"', '"')
                            tokens.append((token_type, value))
                        elif 'number' in groups and groups['number']:
                            tokens.append((token_type, float(groups['number'])))
                        elif 'path' in groups and groups['path']:
                            tokens.append((token_type, groups['path']))
                        elif 'expr' in groups and groups['expr']:
                            tokens.append((token_type, groups['expr']))
                        else:
                            tokens.append((token_type, match.group()))
                    self.pos = match.end()
                    break
            else:
                raise FFmpegError(
                    code="LEXER_ERROR",
                    message=f"无法识别的字符: {self.text[self.pos]}",
                    suggestion=f"请检查'{self.text[self.pos]}'附近的语法，确保使用了正确的FFmpeg选项和滤镜参数",
                    level=ErrorLevel.CRITICAL
                )

        tokens.append((FilterTokenType.EOF, ""))
        return tokens