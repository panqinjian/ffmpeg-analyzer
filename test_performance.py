import unittest
import time
import cProfile
import pstats
import io
from core.command_builder import CommandBuilder
from parsers.semantic_analyzer import SemanticAnalyzer
from parsers.parser_models import ParsedCommand

import os
import sys

if __name__ == "__main__":
    os.environ['DEBUG_MODE'] = 'True'
    os.chdir('D:\\AI\\Comfyui_Nvidia\\')
    class_path = os.path.join(os.getcwd(), "custom_nodes","comfyui_ffmpeg_deepseek")
    sys.path.append(class_path)
    from loader import init_plugins
    init_plugins()

from parsers.lexer.filter_lexer import FilterLexer

class TestLexerPerformance(unittest.TestCase):
    def test_small_input_performance(self):
        """测试小规模输入性能"""
        input_str = "[0:v]scale=1280:720[out]"
        time_taken = timeit.timeit(
            lambda: FilterLexer(input_str).tokenize(),
            number=1000
        )
        self.assertLess(time_taken, 1.0, "处理1000次小规模输入应小于1秒")

    def test_large_input_performance(self):
        """测试大规模输入性能"""
        input_str = "[0:v]" + ",".join([f"scale={w}:{h}" for w, h in zip(range(100, 1100, 100), range(100, 1100, 100))]) + "[out]"
        time_taken = timeit.timeit(
            lambda: FilterLexer(input_str).tokenize(),
            number=100
        )
        self.assertLess(time_taken, 2.0, "处理100次大规模输入应小于2秒")

class TestPerformance(unittest.TestCase):
    def setUp(self):
        self.builder = CommandBuilder()
        self.analyzer = SemanticAnalyzer()
        
    def test_command_building_performance(self):
        """测试命令构建性能"""
        start_time = time.time()
        
        # 构建一个复杂的命令
        for _ in range(1000):
            command = (self.builder
                      .input("input.mp4")
                      .filter("scale", width=1280, height=720)
                      .filter("format", pix_fmt="yuv420p")
                      .filter("colorbalance", rs=0.5, gs=0.5, bs=0.5)
                      .output("output.mp4")
                      .build())
        
        duration = time.time() - start_time
        self.assertLess(duration, 1.0)  # 应该在1秒内完成
        
    def test_semantic_analysis_performance(self):
        """测试语义分析性能"""
        pr = cProfile.Profile()
        pr.enable()
        
        # 创建测试命令
        command = ParsedCommand(
            streams=[{"id": "0:v", "type": "video"}],
            filter_chains=[{
                "inputs": ["0:v"],
                "output": "out",
                "filters": [
                    {"name": "scale", "params": {"width": "1280", "height": "720"}},
                    {"name": "format", "params": {"pix_fmt": "yuv420p"}},
                    {"name": "colorbalance", "params": {"rs": "0.5", "gs": "0.5", "bs": "0.5"}}
                ]
            }],
            outputs=[{"file": "output.mp4"}]
        )
        
        # 执行性能测试
        for _ in range(100):
            self.analyzer.validate(command)
        
        pr.disable()
        s = io.StringIO()
        ps = pstats.Stats(pr, stream=s).sort_stats('cumulative')
        ps.print_stats()
        
        # 检查性能统计
        stats = s.getvalue()
        self.assertIn('validate', stats)
        self.assertLess(float(stats.split()[0]), 1.0)  # 总时间应小于1秒

if __name__ == '__main__':
    unittest.main()
