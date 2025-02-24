from dataclasses import dataclass
from typing import List
import os
import sys

class_path = os.path.join(os.getcwd(), "custom_nodes","ffmpeg-analyzer")
sys.path.append(class_path)
from __init__ import ClassImporter 
importer = ClassImporter()
importer.class_import(["filter_registry.py", "error_types.py"])
from filters.filter_registry import register_filter, FilterSpec

@dataclass
class FormatParams:
    format: str

@register_filter("format")
class FormatFilter:
    spec = FilterSpec(
        required_params=["format"],
        optional_params=[],
        param_ranges={}
    )

    def __init__(self, params: FormatParams):
        self.params = params

    def apply(self):
        # 这里可以实现格式转换的逻辑
        pass
