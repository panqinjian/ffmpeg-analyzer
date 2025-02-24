import os
import sys
import inspect

if os.getenv('DEBUG_MODE', 'False') == 'True':
    os.chdir('D:\\AI\\Comfyui_Nvidia\\')
    class_path = os.path.join(os.getcwd(), "custom_nodes","comfyui_ffmpeg_deepseek")
    sys.path.append(class_path)
    from loader import init_plugins
    init_plugins()

from dataclasses import dataclass
from typing import List, Optional, Dict, Callable
from lexer.filter_lexer import FilterLexer
from filters.video.format_filter import FormatFilter

@dataclass
class FilterSpec:
    required_params: List[str]
    optional_params: List[str] = None
    param_ranges: Optional[Dict] = None
    gpu_mapping: Optional[str] = None

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

class FilterRegistry:
    _registry = {}

    @classmethod
    def register(cls, name: str):
        def decorator(filter_cls):
            if not inspect.isclass(filter_cls) or not hasattr(filter_cls, 'spec'):
                raise ValueError("滤镜类必须包含spec属性和验证方法")
            cls._registry[name] = filter_cls
            return filter_cls
        return decorator

    @classmethod
    def get_filter(cls, filter_name: str):
        try:
            # 使用 FFmpeg 命令行检查滤镜是否存在
            result = subprocess.run(['ffmpeg', '-filters'], capture_output=True, text=True, check=True)
            print(f"FFmpeg 滤镜列表: {result.stdout}")  # 打印调试信息
            if filter_name in result.stdout:
                return cls._registry.get(filter_name, None)
            return None
        except subprocess.CalledProcessError as e:
            print(f"FFmpeg 命令执行失败: {e.stderr}")  # 打印错误信息
            return None

    @classmethod
    def get_spec(cls, name: str) -> FilterSpec:
        print(f"检索滤镜规格: {name}")  # 
        print(f"FILTER_SPECS 内容: {FILTER_SPECS}")  # 
        filter_cls = cls.get_filter(name)
        spec = filter_cls.spec if filter_cls else FILTER_SPECS.get(name)
        print(f"返回的滤镜规格: {spec}")  # 
        return spec

# 注册 scale 滤镜
FilterRegistry._registry["scale"] = {
    "required_params": ["width", "height"],
    "param_ranges": {
        "width": (1, 8192),
        "height": (1, 8192)
    }
}

# 
register_filter = FilterRegistry.register
get_filter_spec = FilterRegistry.get_spec

register_filter("format")(FormatFilter)