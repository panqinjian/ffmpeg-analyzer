

import os
import sys
class_path = os.path.join(os.getcwd(), "custom_nodes","ffmpeg-analyzer")
sys.path.append(class_path)
from __init__ import ClassImporter 
importer = ClassImporter()
importer.class_import(["command_processor.py"])

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