import os
import sys
import logging
import subprocess
from typing import Dict, Optional
from core.error_types import FFmpegError, ErrorType

class IntelQSVAccelerator:
    """Intel QSV 加速器"""
    
    SUPPORTED_FILTERS = {
        'scale': {
            'impl': 'scale_qsv',
            'params': {'w': 'width', 'h': 'height'},
            'requires': ['-hwaccel qsv']
        },
        'overlay': {
            'impl': 'overlay_qsv',
            'params': {'x': 'x', 'y': 'y'}
        }
    }

    def __init__(self):
        self.video_codec = "h264_qsv"
        self.device_id = 0
        self._check_driver()
        
    def is_available(self) -> bool:
        """检查是否可用QSV加速"""
        try:
            self._check_driver()
            return True
        except FFmpegError:
            return False

    def optimize_filter(self, filter_str: str) -> Optional[str]:
        """优化滤镜命令"""
        name, params = self._parse_filter(filter_str)
        if spec := self.SUPPORTED_FILTERS.get(name):
            param_mapping = ":".join(
                f"{spec['params'][k]}={v}"
                for k, v in params.items()
                if k in spec['params']
            )
            return f"{spec['impl']}={param_mapping}"
        return None

    def _parse_filter(self, filter_str: str) -> tuple:
        """解析滤镜字符串"""
        if '=' in filter_str:
            name, param_part = filter_str.split('=', 1)
            params = dict(p.split('=') for p in param_part.split(':'))
        else:
            name, params = filter_str, {}
        return name.strip(), params

    def _check_driver(self) -> None:
        """检查驱动是否可用"""
        try:
            output = subprocess.check_output(
                ["vainfo"], 
                text=True, 
                stderr=subprocess.STDOUT
            )
            if "iHD" not in output:
                raise FFmpegError(
                    "Intel iHD驱动未安装",
                    error_type=ErrorType.DRIVER_MISSING,
                    suggestion="安装intel-media-va-driver"
                )
        except FileNotFoundError:
            raise FFmpegError(
                "未检测到VAAPI支持",
                error_type=ErrorType.HARDWARE_UNAVAILABLE,
                suggestion="安装vainfo和intel-media-va-driver"
            )