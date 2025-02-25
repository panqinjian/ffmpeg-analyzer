import unittest
import logging
import traceback
import os
import sys
from unittest.mock import patch
from loader import init_plugins
from parsers.semantic_analyzer import SemanticAnalyzer
from parsers.parser_models import ParsedCommand
from core.error_types import FFmpegError

class TestSemanticAnalyzer(unittest.TestCase):
    def setUp(self):
        self.analyzer = SemanticAnalyzer()
        
    def test_stream_validation(self):
        """测试流标签验证"""
        # 有效的命令
        valid_command = ParsedCommand(
            streams=[{"id": "0:v", "type": "video"}],
            filter_chains=[{
                "inputs": ["0:v"],
                "output": "out",
                "filters": [{"name": "scale", "params": {"width": "1280", "height": "720"}}]
            }],
            outputs=[{"file": "output.mp4"}]
        )
        self.assertTrue(self.analyzer.validate(valid_command))
        
        # 无效的命令 - 未定义的输入流
        invalid_command = ParsedCommand(
            streams=[],
            filter_chains=[{
                "inputs": ["1:v"],  # 未定义的流
                "output": "out",
                "filters": []
            }],
            outputs=[]
        )
        with self.assertRaises(FFmpegError) as context:
            self.analyzer.validate(invalid_command)
        self.assertIn("未定义的输入流", str(context.exception))

if __name__ == "__main__":
    # 设置环境变量
    os.environ['DEBUG_MODE'] = 'True'
    
    # 设置工作目录
    os.chdir('D:\\AI\\Comfyui_Nvidia\\')
    
    # 初始化插件
    init_plugins()
    
    # 运行测试
    unittest.main()
   

