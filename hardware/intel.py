import subprocess
import re

import sys
import os

class_path = os.path.join(os.getcwd(), "custom_nodes","ffmpeg-analyzer")
sys.path.append(class_path)
from __init__ import ClassImporter 
importer = ClassImporter()
importer.class_import(["error_types.py"])

class IntelQSVAccelerator:
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
        self._check_driver()
        self._devices = self._get_qsv_devices()

    def is_available(self) -> bool:
        return len(self._devices) > 0

    def optimize_filter(self, filter_str: str) -> str:
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
        if '=' in filter_str:
            name, param_part = filter_str.split('=', 1)
            params = dict(p.split('=') for p in param_part.split(':'))
        else:
            name, params = filter_str, {}
        return name.strip(), params

    def _check_driver(self):
        try:
            output = subprocess.check_output(
                ["vainfo"], 
                text=True, 
                stderr=subprocess.STDOUT
            )
            if "iHD" not in output:
                raise FFmpegError(
                    code="QSV_DRIVER_MISSING",
                    message="Intel iHD驱动未安装",
                    suggestion="安装intel-media-va-driver",
                    level=ErrorLevel.CRITICAL
                )
        except FileNotFoundError:
            raise FFmpegError(
                code="VAAPI_UNAVAILABLE",
                message="未检测到VAAPI支持",
                suggestion="安装vainfo和intel-media-va-driver",
                level=ErrorLevel.CRITICAL
            )

    def _get_qsv_devices(self) -> list:
        try:
            output = subprocess.check_output(
                ["ls /dev/dri/renderD*"], 
                shell=True, 
                text=True
            )
            return output.strip().split()
        except subprocess.CalledProcessError:
            return []