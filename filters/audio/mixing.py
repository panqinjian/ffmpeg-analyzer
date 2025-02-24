from dataclasses import dataclass
from typing import List

import os
import sys

class_path = os.path.join(os.getcwd(), "custom_nodes","ffmpeg-analyzer")
sys.path.append(class_path)
from __init__ import ClassImporter 
importer = ClassImporter()
importer.class_import(["filter_registry.py", "error_types.py"])
from filters.filter_registry import FilterSpec

@dataclass
class MixParams:
    inputs: int
    duration: str = "longest"
    weights: List[float] = None

@register_filter("amix")
class AudioMixer:
    spec = FilterSpec(
        required_params=["inputs"],
        optional_params=["duration", "weights"],
        param_ranges={
            "inputs": (2, 32),
            "duration": ["longest", "shortest", "first"],
            "weights": None
        }
    )

    def __init__(self, params: dict):
        self.params = MixParams(**params)

    def validate(self):
        if self.params.inputs < 2:
            raise FFmpegError(
                code="MIN_INPUTS",
                message="混音需要至少2个输入流",
                suggestion="检查输入音频流数量",
                level=ErrorLevel.CRITICAL
            )
        
        if self.params.weights and len(self.params.weights) != self.params.inputs:
            raise FFmpegError(
                code="WEIGHT_MISMATCH",
                message="权重数量与输入流不一致",
                suggestion=f"需要 {self.params.inputs} 个权重值",
                level=ErrorLevel.CRITICAL
            )

    def generate(self) -> str:
        params = [f"inputs={self.params.inputs}", f"duration={self.params.duration}"]
        if self.params.weights:
            params.append(f"weights={'|'.join(map(str, self.params.weights))}")
        return f"amix={':'.join(params)}"