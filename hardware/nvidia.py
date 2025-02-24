import subprocess


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
        # 处理逻辑，返回正确的滤镜字符串
        filter_name, params = self._parse_filter(filter_str)
        if filter_name in self.SUPPORTED_FILTERS:
            supported_filter = self.SUPPORTED_FILTERS[filter_name]
            optimized_params = {supported_filter['params'][k]: v for k, v in params.items() if k in supported_filter['params']}
            optimized_filter_str = f"{supported_filter['impl']}={':'.join(f'{k}={v}' for k, v in optimized_params.items())}"
            if 'requires' in supported_filter:
                optimized_filter_str += f",hwaccel={supported_filter['requires'][0].split('=')[1]}"
            return optimized_filter_str
        else:
            return filter_str

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