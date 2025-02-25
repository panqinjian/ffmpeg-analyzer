import os
import sys
import inspect
import subprocess
from dataclasses import dataclass
from typing import List, Optional, Dict, Callable
from core.error_types import FFmpegError, ErrorType
from parsers.lexer.filter_lexer import FilterLexer
from parsers.lexer.token_types import FilterTokenType
from filters.video.format_filter import FormatFilter
from parsers.parser_models import FilterNode

@dataclass
class FilterSpec:
    required_params: List[str]
    optional_params: List[str] = None
    param_ranges: Optional[Dict] = None
    gpu_mapping: Optional[str] = None

class FilterRegistry:
    """滤镜注册表"""
    
    _instance = None
    _filters = {}  # 类变量存储滤镜
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._initialized = False
        return cls._instance
    
    def __init__(self):
        if not self._initialized:
            self.lexer = FilterLexer()
            self._initialized = True
    
    @classmethod
    def register(cls, name: str):
        """注册滤镜装饰器"""
        def decorator(filter_cls):
            if not inspect.isclass(filter_cls) or not hasattr(filter_cls, 'spec'):
                raise ValueError("滤镜类必须包含spec属性和验证方法")
            cls._filters[name] = filter_cls
            return filter_cls
        return decorator

    @classmethod
    def get_filter(cls, filter_name: str):
        """获取滤镜"""
        try:
            result = subprocess.run(['ffmpeg', '-filters'], 
                                 capture_output=True, 
                                 text=True, 
                                 check=True)
            if filter_name in result.stdout:
                return cls._filters.get(filter_name, None)
            return None
        except subprocess.CalledProcessError as e:
            print(f"FFmpeg 命令执行失败: {e.stderr}")
            return None

    @classmethod
    def get_spec(cls, name: str) -> Optional[FilterSpec]:
        """获取滤镜规格"""
        filter_cls = cls.get_filter(name)
        if filter_cls:
            return filter_cls.spec
        return FILTER_SPECS.get(name)

# 预定义的滤镜规格
FILTER_SPECS = {
    'scale': FilterSpec(
        required_params=['width', 'height'],
        param_ranges={
            'width': (1, 8192),
            'height': (1, 8192)
        }
    ),
    'format': FilterSpec(
        required_params=['pix_fmt'],
        param_ranges={
            'pix_fmt': ('yuv420p', 'rgb24', 'gray')
        }
    ),
    'volume': FilterSpec(
        required_params=['volume'],
        param_ranges={
            'volume': (0.0, 10.0)
        }
    ),
    'rotate': FilterSpec(
        required_params=['angle'],
        param_ranges={
            'angle': (0.0, 360.0)
        }
    ),
    'eq': FilterSpec(
        required_params=[],
        param_ranges={
            'brightness': (-1.0, 1.0),
            'contrast': (0.0, 2.0)
        }
    )
}

# 注册基本滤镜
FilterRegistry._filters.update({
    "scale": {
        "required_params": ["width", "height"],
        "param_ranges": {
            "width": (1, 8192),
            "height": (1, 8192)
        }
    }
})

# 注册format滤镜
register_filter = FilterRegistry.register
get_filter_spec = FilterRegistry.get_spec

register_filter("format")(FormatFilter)

# 确保导出所需的内容
__all__ = ['FilterRegistry', 'FilterSpec', 'register_filter', 'get_filter_spec']