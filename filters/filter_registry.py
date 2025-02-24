import os
import sys
import logging
import inspect
from dataclasses import dataclass
from typing import Dict, List, Optional, Union

@dataclass
class FilterSpec:
    required_params: List[str]
    optional_params: List[str] = None
    param_ranges: Optional[Dict] = None
    gpu_mapping: Optional[str] = None

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
    def get_filter(cls, name: str):
        return cls._registry.get(name)

    @classmethod
    def get_spec(cls, name: str) -> FilterSpec:
        filter_cls = cls.get_filter(name)
        return filter_cls.spec if filter_cls else None

# 快捷装饰器
register_filter = FilterRegistry.register
get_filter_spec = FilterRegistry.get_spec