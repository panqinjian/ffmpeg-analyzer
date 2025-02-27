from core.command_processor import FFmpegCommandProcessor
from core.error_types import FFmpegError, ErrorLevel
import shlex
from typing import Dict, Any, List
from core.command_builder import CommandBuilder
from parsers.semantic_analyzer import SemanticAnalyzer

class FFmpegProcessingNode:
    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "input_video": ("STRING", {"default": ""}),
                "filter_chain": ("STRING", {"multiline": True}),
                "enable_gpu": ("BOOLEAN", {"default": True})
            },
            "optional": {
                "audio_input": ("STRING", {"default": ""})
            }
        }

    RETURN_TYPES = ("VIDEO_STREAM", "AUDIO_STREAM")
    RETURN_NAMES = ("video", "audio")
    CATEGORY = "FFmpeg/Processing"

    def process(self, input_video: str, filter_chain: str, enable_gpu: bool, audio_input: str = ""):
        # 构建基础命令
        cmd = ["ffmpeg -y"]
        if input_video:
            cmd.append(f"-i {shlex.quote(input_video)}")
        if audio_input:
            cmd.append(f"-i {shlex.quote(audio_input)}")
        
        cmd.append(f"-filter_complex {shlex.quote(filter_chain)}")
        
        # 处理输出
        processor = FFmpegCommandProcessor(enable_hw_accel=enable_gpu)
        result = processor.process(" ".join(cmd))
        
        if result["status"] != "success":
            raise Exception(f"FFmpeg处理失败: {result.get('message', '未知错误')}")
        
        return (result["output_path"], result.get("audio_path", ""))

class FFmpegAdvancedProcessing:
    """FFmpeg高级处理节点"""
    
    def __init__(self):
        self.builder = CommandBuilder()
        self.analyzer = SemanticAnalyzer()
        
    def process(self, input_file: str, filters: List[Dict[str, Any]], output_file: str) -> str:
        """处理视频"""
        try:
            command = (self.builder
                      .input(input_file)
                      .filters(filters)
                      .output(output_file)
                      .build())
            
            # 验证命令
            self.analyzer.validate(command)
            
            return command
        except FFmpegError as e:
            raise FFmpegError(
                f"处理失败: {str(e)}",
                error_type="PROCESSING_ERROR",
                suggestion=e.suggestion
            )

# 确保导出类
__all__ = ['FFmpegAdvancedProcessing']