import unittest

import os
import sys

if __name__ == "__main__":
    os.environ['DEBUG_MODE'] = 'True'
    os.chdir('D:\\AI\\Comfyui_Nvidia\\')
    class_path = os.path.join(os.getcwd(), "custom_nodes","comfyui_ffmpeg_deepseek")
    sys.path.append(class_path)
    from loader import init_plugins
    init_plugins()
from core.error_types import FFmpegError, ErrorLevel
from parsers.semantic_analyzer import SemanticAnalyzer
from parsers.parser_models import ParsedCommand, FilterNode, Stream
from parsers.filter_parser import FilterParser

class TestSemanticAnalysis(unittest.TestCase):
    def setUp(self):
        self.analyzer = SemanticAnalyzer()
        self.parser = FilterParser()

    def test_stream_label_lifecycle(self):
        # 创建 ParsedCommand 实例
        parsed_command = ParsedCommand(
            inputs=["input.mp4"],
            outputs=["output.mp4"],
            global_options={"y": ""},
            filter_chains=[
                [FilterNode(name="format", params={"pix_fmts": "rgba"}, inputs=[Stream(type="v", label="0:v")], outputs=[])]
            ]
        )

        # 调用 validate 方法
        warnings = self.analyzer.validate(parsed_command)
        print("Warnings:", warnings)
        assert warnings == []

    def test_stream_label_lifecycle(self):
        # 示例命令（确保流标签 [outv] 和 [aout] 正确定义并使用）
        command = (
            "[0:v]scale=iw/2:ih/2[base1];"
            "[v2]scale=iw/2:ih/2[base2];"
            "[base1][base2]hstack[outv];"
            "[1:a]volume=1.0[a1];"
            "[0:a][a1]amix=inputs=2[aout]"
        )
        parsed_command = self.parser.parse(command)
        warnings = self.analyzer.validate(parsed_command)
        self.assertEqual(warnings, [])  # 预期无警告

    def test_filter_parameter_validation(self):
        """测试滤镜参数验证"""
        parsed_command = ParsedCommand(
            inputs=["input.mp4"],
            outputs=["output.mp4"],
            global_options={"y": ""},
            filter_chains=[
                [FilterNode(name="scale", params={"width": 1280, "height": 720}, inputs=[Stream(type="v", label="0:v")], outputs=[])]
            ]
        )
        self.analyzer.validate(parsed_command)

    def test_output_mapping_validation(self):
        """测试输出映射验证"""
        parsed_command = ParsedCommand(
            inputs=["input.mp4"],
            outputs=["output.mp4"],
            global_options={"y": ""},
            filter_chains=[
                [FilterNode(name="scale", params={"width": 1280, "height": 720}, inputs=[Stream(type="v", label="0:v")], outputs=[Stream(type="v", label="[outv]")])]
            ]
        )
        self.analyzer.validate(parsed_command)

    def test_error_handling(self):
        """测试错误处理"""
        parsed_command = ParsedCommand(
            inputs=["input.mp4"],
            outputs=["output.mp4"],
            global_options={"y": ""},
            filter_chains=[
                [FilterNode(name="scale", params={"width": 1280, "height": 720}, inputs=[Stream(type="v", label="undefined")], outputs=[])]
            ]
        )
        with self.assertRaises(FFmpegError):
            self.analyzer.validate(parsed_command)

if __name__ == '__main__':
    unittest.main()
