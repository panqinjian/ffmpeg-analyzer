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
        print(error)

    def test_error_level_validation(self):
        """测试错误级别验证"""
        self.assertTrue(ErrorLevel.CRITICAL.value > ErrorLevel.WARNING.value)
        self.assertTrue(ErrorLevel.INFO.value > ErrorLevel.WARNING.value)
if __name__ == '__main__':
    unittest.main()
