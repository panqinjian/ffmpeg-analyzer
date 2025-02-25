from typing import Dict, Any, List, Optional
from dataclasses import dataclass
from core.error_types import FFmpegError, ErrorLevel

@dataclass
class WidgetConfig:
    """小部件配置"""
    type: str
    label: str
    default: Any
    options: Optional[List[str]] = None
    min_value: Optional[float] = None
    max_value: Optional[float] = None
    step: Optional[float] = None

class FFmpegWidget:
    """FFmpeg参数小部件基类"""
    def __init__(self, config: WidgetConfig):
        self.config = config
        self.value = config.default
        
    def get_value(self) -> Any:
        return self.value
        
    def set_value(self, value: Any) -> None:
        self.value = value
        
    def to_dict(self) -> Dict[str, Any]:
        return {
            "type": self.config.type,
            "label": self.config.label,
            "value": self.value
        }

class NumberWidget(FFmpegWidget):
    """数值输入小部件"""
    def set_value(self, value: Any) -> None:
        try:
            num_value = float(value)
            if (self.config.min_value is not None and num_value < self.config.min_value or
                self.config.max_value is not None and num_value > self.config.max_value):
                raise ValueError("Value out of range")
            self.value = num_value
        except (ValueError, TypeError):
            raise ValueError(f"Invalid number value: {value}")

class SelectWidget(FFmpegWidget):
    """下拉选择小部件"""
    def set_value(self, value: str) -> None:
        if value not in self.config.options:
            raise ValueError(f"Invalid option: {value}")
        self.value = value

class TextWidget(FFmpegWidget):
    """文本输入小部件"""
    pass

# 导出所有小部件类
__all__ = ['WidgetConfig', 'FFmpegWidget', 'NumberWidget', 'SelectWidget', 'TextWidget']