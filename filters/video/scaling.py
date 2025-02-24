from typing import Union
from dataclasses import dataclass
import os
import sys

class_path = os.path.join(os.getcwd(), "custom_nodes","ffmpeg-analyzer")
sys.path.append(class_path)
from __init__ import ClassImporter 
importer = ClassImporter()
importer.class_import(["filter_registry.py", "error_types.py"])
from filters.video import *
from core.error_types import FFmpegError, ErrorLevel
from filter_registry import FilterRegistry,FilterSpec, get_filter_spec, register_filter
from filters.video import *

@dataclass
class ScaleParams:
    width: Union[int, str]
    height: Union[int, str]
    flags: str = "bilinear"
    gpu: bool = False

@register_filter("scale")
class ScaleFilter:
    spec = FilterSpec(
        required_params=["width", "height"],
        optional_params=["flags"],
        param_ranges={
            "width": (1, 7680),
            "height": (1, 4320),
            "flags": ["bilinear", "bicubic", "lanczos"]
        },
        gpu_mapping="scale_{hw}"
    )

    def __init__(self, params: dict):
        self.params = ScaleParams(**params)

    def validate(self):
        if isinstance(self.params.width, str) and not self.params.width.startswith("iw"):
            raise FFmpegError(
                code="INVALID_WIDTH",
                message=f"非法宽度表达式: {self.params.width}",
                suggestion="使用类似iw/2的表达式或具体数值",
                level=ErrorLevel.CRITICAL
            )
        
        if self.params.flags not in self.spec.param_ranges["flags"]:
            raise FFmpegError(
                code="INVALID_SCALE_FLAG",
                message=f"不支持的缩放算法: {self.params.flags}",
                suggestion=f"可选值: {', '.join(self.spec.param_ranges['flags'])}",
                level=ErrorLevel.WARNING
            )

    def generate(self, hw_accel: str = None) -> str:
        if hw_accel and self.spec.gpu_mapping:
            impl = self.spec.gpu_mapping.replace("{hw}", hw_accel)
            return f"{impl}=w={self.params.width}:h={self.params.height}"
        return f"scale=w={self.params.width}:h={self.params.height}:flags={self.params.flags}"