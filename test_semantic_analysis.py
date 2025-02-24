import unittest

import os
import sys

os.environ['DEBUG_MODE'] = 'True'
os.environ['DEBUG_path'] = 'D:\\AI\\Comfyui_Nvidia\\'
is_debug_mode = os.getenv('DEBUG_MODE', 'False') == 'True'
os.chdir('D:\\AI\\Comfyui_Nvidia\\')

class_path = os.path.join(os.getcwd(), "custom_nodes","comfyui_ffmpeg_deepseek")
sys.path.append(class_path)
from __init__ import ClassImporter 
importer = ClassImporter()
importer.class_import(["semantic_analyzer.py", "error_types.py", "filter_registry.py"])
from core.error_types import FFmpegError, ErrorLevel
from parsers.semantic_analyzer import SemanticAnalyzer
from parsers.filter_registry import FilterRegistry, get_filter_spec


class TestSemanticAnalysis(unittest.TestCase):
    def setUp(self):
        self.analyzer = SemanticAnalyzer()

    def test_stream_label_lifecycle(self):
        """测试流标签生命周期验证"""
        parsed_command = {
            "filter_chains": [
                {
                    "inputs": ["0:v"],
                    "filters": ["scale=1280:720"],
                    "output": "[outv]"
                },
                {
                    "inputs": ["[outv]"],
                    "filters": ["format=yuv420p"],
                    "output": "[final]"
                }
            ],
            "outputs": [{"map": "[final]"}]
        }
        warnings = self.analyzer.validate(parsed_command)
        if warnings and 'error' in warnings:
            print("测试失败:", warnings)
        else:
            print("测试成功")

    def test_filter_parameter_validation(self):
        """测试滤镜参数验证"""
        parsed_command = {
            "filter_chains": [
                {
                    "inputs": ["0:v"],
                    "filters": ["scale=width=1280:height=720"],
                    "output": "[outv]"
                }
            ]
        }
        self.analyzer.validate(parsed_command)

    def test_output_mapping_validation(self):
        """测试输出映射验证"""
        parsed_command = {
            "filter_chains": [
                {
                    "inputs": ["0:v"],
                    "filters": ["scale=1280:720"],
                    "output": "[outv]"
                }
            ],
            "outputs": [{"map": "[outv]"}]
        }
        self.analyzer.validate(parsed_command)

    def test_error_handling(self):
        """测试错误处理"""
        parsed_command = {
            "filter_chains": [
                {
                    "inputs": ["undefined"],
                    "filters": ["scale=1280:720"],
                    "output": "[outv]"
                }
            ]
        }
        with self.assertRaises(FFmpegError):
            self.analyzer.validate(parsed_command)

if __name__ == '__main__':
    unittest.main()
