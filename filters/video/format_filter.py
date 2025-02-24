from dataclasses import dataclass
from typing import List
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
