from enum import Enum
from dataclasses import dataclass
from typing import Optional, Dict, Any

class ErrorLevel(Enum):
    WARNING = "WARNING"
    ERROR = "ERROR"
    CRITICAL = "CRITICAL"

class ErrorType(Enum):
    """错误类型常量"""
    LEXER_ERROR = "LEXER_ERROR"
    PARSER_ERROR = "PARSER_ERROR"
    VALIDATION_ERROR = "VALIDATION_ERROR"
    UNKNOWN_ERROR = "UNKNOWN_ERROR"
    INVALID_PARAM = "INVALID_PARAM"
    UNKNOWN_FILTER = "UNKNOWN_FILTER"
    FORMAT_MISMATCH = "FORMAT_MISMATCH"
    HW_NOT_SUPPORTED = "HW_NOT_SUPPORTED"
    SEMANTIC_ERROR = "SEMANTIC_ERROR"

@dataclass
class FFmpegError(Exception):
    message: str
    error_type: str = "UNKNOWN_ERROR"
    suggestion: Optional[str] = None
    details: Optional[Dict[str, Any]] = None
    level: str = "ERROR"

    def __str__(self):
        return f"{self.error_type}: {self.message}"

# 确保导出类
__all__ = ['FFmpegError', 'ErrorType']