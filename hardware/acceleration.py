import os
import sys
import logging
import inspect
from dataclasses import dataclass
from typing import Dict, List, Optional, Union
from core.error_types import FFmpegError, ErrorType
from hardware.nvidia import CUDAAccelerator
from hardware.intel import IntelQSVAccelerator

class AccelerationManager:
    """硬件加速管理器"""
    PRIORITY = ['cuda', 'qsv', 'vaapi']

    def __init__(self):
        self.accelerators = {
            'cuda': CUDAAccelerator(),
            'qsv': IntelQSVAccelerator()
        }
        self.active_accelerator = self._detect_accelerator()

    def _detect_accelerator(self) -> Optional[str]:
        for hw in self.PRIORITY:
            if self.accelerators[hw].is_available():
                return hw
        return None

    def optimize_command(self, parsed_command: Dict) -> Dict:
        if not self.active_accelerator:
            return parsed_command
        
        accelerator = self.accelerators[self.active_accelerator]
        
        # 优化滤镜链
        for chain in parsed_command.get("filter_chains", []):
            chain["filters"] = [
                accelerator.optimize_filter(f) 
                for f in chain["filters"]
                if accelerator.optimize_filter(f) is not None
            ]
        
        # 设置编码器
        if "outputs" in parsed_command:
            for output in parsed_command["outputs"]:
                if "video_codec" in output:
                    output["video_codec"] = accelerator.video_codec
        
        return parsed_command

    def get_current_accelerator(self) -> str:
        return self.active_accelerator or "software"

# 确保导出类
__all__ = ['AccelerationManager']