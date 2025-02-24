import subprocess
import sys
import os


class_path = os.path.join(os.getcwd(), "custom_nodes","ffmpeg-analyzer")
sys.path.append(class_path)
from __init__ import ClassImporter 
importer = ClassImporter()
importer.class_import(["error_types.py"])

#class_path = FileUtils.find_file_path("error_types.py")
#sys.path.append(class_path)
#from error_types import FFmpegError, ErrorLevel


class CUDAAccelerator:
    SUPPORTED_FILTERS = {
        'scale': {
            'impl': 'scale_cuda',
            'params': {'w': 'width', 'h': 'height'},
            'requires': ['hwaccel=cuda']
        },
        'overlay': {
            'impl': 'overlay_cuda',
            'params': {'x': 'x', 'y': 'y'}
        }
    }

    def __init__(self):
        self._check_driver()
        self._devices = self._get_cuda_devices()

    def is_available(self) -> bool:
        return len(self._devices) > 0

    def optimize_filter(self, filter_str: str) -> str:
        """将滤镜转换为CUDA实现"""
        name, params = self._parse_filter(filter_str)
        if spec := self.SUPPORTED_FILTERS.get(name):
            return f"{spec['impl']}=" + ":".join(
                f"{spec['params'][k]}={v}" 
                for k, v in params.items()
                if k in spec['params']
            )
        return None

    def _parse_filter(self, filter_str: str) -> tuple:
        name, param_str = filter_str.split('=', 1) if '=' in filter_str else (filter_str, "")
        params = dict(p.split('=') for p in param_str.split(':'))
        return name.strip(), params

    def _check_driver(self):
        try:
            subprocess.run(
                ["nvidia-smi"], 
                check=True, 
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL
            )
        except (subprocess.CalledProcessError, FileNotFoundError):
            raise FFmpegError(
                code="CUDA_UNAVAILABLE",
                message="NVIDIA驱动未安装或不可用",
                suggestion="安装nvidia-driver和CUDA工具包",
                level=ErrorLevel.CRITICAL
            )

    def _get_cuda_devices(self) -> list:
        try:
            output = subprocess.check_output(
                ["nvidia-smi", "-L"], 
                text=True
            )
            return [line.split(":")[0] for line in output.strip().split("\n")]
        except:
            return []