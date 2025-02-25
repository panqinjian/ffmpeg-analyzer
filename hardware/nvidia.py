from typing import Dict, Optional
from core.error_types import FFmpegError, ErrorType

class CUDAAccelerator:
    """NVIDIA CUDA 加速器"""
    
    def __init__(self):
        self.video_codec = "h264_nvenc"
        self.device_id = 0
    
    def is_available(self) -> bool:
        """检查是否可用CUDA加速"""
        try:
            import torch
            return torch.cuda.is_available()
        except ImportError:
            return False
    
    def optimize_filter(self, filter_def: Dict) -> Optional[Dict]:
        """优化滤镜配置"""
        name = filter_def["name"]
        if name == "scale":
            filter_def["name"] = "scale_cuda"
        elif name == "format":
            filter_def["name"] = "format_cuda"
        return filter_def
    
    def get_device_info(self) -> Dict:
        """获取设备信息"""
        try:
            import torch
            return {
                "name": torch.cuda.get_device_name(self.device_id),
                "memory": torch.cuda.get_device_properties(self.device_id).total_memory,
                "capability": torch.cuda.get_device_capability(self.device_id)
            }
        except ImportError:
            return {}

# 确保导出类
__all__ = ['CUDAAccelerator']