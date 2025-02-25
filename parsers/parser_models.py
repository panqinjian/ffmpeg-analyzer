from typing import List, Dict, Optional, Any
from dataclasses import dataclass

@dataclass
class Stream:
    id: str
    type: str  # "video" 或 "audio"

@dataclass
class FilterNode:
    name: str
    params: Dict[str, str]
    inputs: List[str]
    outputs: List[str]

@dataclass
class FilterChain:
    inputs: List[str]
    output: str
    filters: List[Dict[str, any]]

@dataclass
class ParseError:
    """解析错误信息"""
    message: str
    line: int
    column: int
    context: str

@dataclass
class ParseResult:
    """解析结果"""
    success: bool
    data: Optional[Dict]
    errors: List[ParseError]

@dataclass
class ParsedCommand:
    """解析后的命令结构"""
    streams: List[Dict]
    filter_chains: List[Dict]
    outputs: List[Dict]

    def to_dict(self) -> Dict:
        """转换为字典格式"""
        return {
            "streams": self.streams,
            "filter_chains": self.filter_chains,
            "outputs": self.outputs
        }

    @classmethod
    def from_dict(cls, data: dict) -> 'ParsedCommand':
        """从字典创建实例"""
        return cls(
            streams=[Stream(**s) for s in data["streams"]],
            filter_chains=[FilterChain(**c) for c in data["filter_chains"]],
            outputs=data["outputs"]
        )

# 确保导出所有需要的类
__all__ = ['Stream', 'FilterNode', 'FilterChain', 'ParseError', 'ParseResult', 'ParsedCommand']
