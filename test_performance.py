import unittest
import timeit

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
importer.class_import(["filter_lexer.py"])

from filter_lexer import FilterLexer

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

if __name__ == '__main__':
    unittest.main()
