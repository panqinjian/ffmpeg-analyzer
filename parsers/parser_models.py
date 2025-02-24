from dataclasses import dataclass, field
from typing import List, Dict, Union

@dataclass
class Stream:
    """表示输入/输出流的标签（如 [0:v], [a1]）"""
    type: str  # 流类型：v（视频）、a（音频）、s（字幕）等
    label: str  # 流标签（如 "0:v", "a1", "outv"）

@dataclass
class FilterNode:
    """表示一个滤镜节点（如 scale=iw/2:ih/2）"""
    name: str           # 滤镜名称（如 "scale"）
    params: Dict[str, str]  # 参数字典（如 {"width": "iw/2", "height": "ih/2"}）
    inputs: List[Stream]    # 输入流列表（如 [Stream(type="v", label="0:v")]）
    outputs: List[Stream]   # 输出流列表（如 [Stream(type="v", label="base1")]）

@dataclass
class ParsedCommand:
    """表示解析后的 FFmpeg 命令结构"""
    inputs: List[str]           # 输入文件列表（如 ["input.mp4"]）
    outputs: List[str]          # 输出文件列表（如 ["output.mp4"]）
    global_options: Dict[str, str]  # 全局选项（如 {"y": "", "hwaccel": "cuda"}）
    filter_chains: List[List[FilterNode]]  # 滤镜链列表（每个链是 FilterNode 的列表）
    
    def get_filters(self) -> List[FilterNode]:
        """获取所有滤镜节点（平铺的列表）"""
        return [node for chain in self.filter_chains for node in chain]
