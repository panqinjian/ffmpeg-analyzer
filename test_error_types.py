import unittest

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
importer.class_import(["error_types.py"])

from error_types import FFmpegError, ErrorLevel

class TestErrorTypes(unittest.TestCase):
    def test_error_definition(self):
        """测试错误类型定义"""
        error = FFmpegError(
            code="TEST_ERROR",
            message="测试错误",
            suggestion="这是一个测试",
            level=ErrorLevel.CRITICAL
        )
        self.assertEqual(error.code, "TEST_ERROR")
        self.assertEqual(error.message, "测试错误")
        self.assertEqual(error.suggestion, "这是一个测试")
        self.assertEqual(error.level, ErrorLevel.CRITICAL)

    def test_error_message_formatting(self):
        """测试错误消息格式化"""
        error = FFmpegError(
            code="TEST_ERROR",
            message="测试错误",
            suggestion="这是一个测试",
            level=ErrorLevel.CRITICAL
        )
        expected = "[TEST_ERROR] 测试错误\n建议: 这是一个测试"
        self.assertEqual(str(error), expected)

    def test_error_level_validation(self):
        """测试错误级别验证"""
        self.assertTrue(ErrorLevel.CRITICAL > ErrorLevel.WARNING)
        self.assertTrue(ErrorLevel.WARNING > ErrorLevel.INFO)

if __name__ == '__main__':
    unittest.main()
