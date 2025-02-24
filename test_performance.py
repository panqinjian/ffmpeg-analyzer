import unittest
import timeit

import os
import sys

if __name__ == "__main__":
    os.environ['DEBUG_MODE'] = 'True'
    os.chdir('D:\\AI\\Comfyui_Nvidia\\')
    class_path = os.path.join(os.getcwd(), "custom_nodes","comfyui_ffmpeg_deepseek")
    sys.path.append(class_path)
    from loader import init_plugins
    init_plugins()

from lexer.filter_lexer import FilterLexer

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
