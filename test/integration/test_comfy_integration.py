import unittest
from core.command_processor import FFmpegCommandProcessor
from core.error_types import FFmpegError, ErrorLevel
import tempfile

import os
import sys

os.environ['DEBUG_MODE'] = 'True'
os.environ['DEBUG_path'] = 'D:\\AI\\Comfyui_Nvidia\\'
is_debug_mode = os.getenv('DEBUG_MODE', 'False') == 'True'
os.chdir('D:\\AI\\Comfyui_Nvidia\\')

class_path = os.path.join(os.getcwd(), "custom_nodes","ffmpeg-analyzer")
sys.path.append(class_path)
from __init__ import ClassImporter 
importer = ClassImporter()
importer.class_import(["nodes.py", "error_types.py"])

class TestComfyIntegration(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        # 创建测试视频文件
        cls.test_video = tempfile.NamedTemporaryFile(suffix=".mp4").name
        with open(cls.test_video, "wb") as f:
            f.write(b"fake video data")

    def test_basic_processing(self):
        """测试基础视频处理流程"""
        node = FFmpegProcessingNode()
        result = node.process(
            input_video=self.test_video,
            filter_chain="[0:v]scale=1280:720[out]",
            enable_gpu=False
        )
        self.assertIn(".mp4", result[0], "应生成MP4输出文件")

    def test_gpu_acceleration(self):
        """测试GPU加速路径"""
        node = FFmpegProcessingNode()
        result = node.process(
            input_video=self.test_video,
            filter_chain="[0:v]scale=1280:720[out]",
            enable_gpu=True
        )
        self.assertIn("nvenc", result[0].lower(), "应使用硬件编码器")

    @classmethod
    def tearDownClass(cls):
        import os
        os.remove(cls.test_video)