from enum import Enum

class ErrorLevel(Enum):
    WARNING = 1
    CRITICAL = 2
    INFO = 3

class FFmpegError(Exception):
    def __str__(self):
        return f"[{self.code}] {self.message}\n建议: {self.suggestion}"
    """FFmpeg命令处理异常基类"""
    def __init__(self, code: str, message: str, suggestion: str, level: ErrorLevel):
        self.code = code
        self.message = message
        self.suggestion = suggestion
        self.level = level
        super().__init__(f"[{code}] {message}")

    def to_dict(self):
        return {
            "code": self.code,
            "message": self.message,
            "suggestion": self.suggestion,
            "level": self.level.name
        }